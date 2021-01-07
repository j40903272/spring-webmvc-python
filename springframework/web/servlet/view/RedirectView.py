import re
from urllib.parse import quote_plus
from springframework.web.servlet import SmartView, View
from springframework.web.servlet.view import AbstractUrlBasedView
from springframework.web.util import WebUtils
from springframework.utils.mock.inst import (
    HttpStatus,
    RequestContextUtils,
    BeanUtils,
    UriComponentsBuilder,
    RequestDataValueProcessor,
    HandlerMapping,
)


class StringBuilder:
    def __init__(self):
        self.s = ""

    def append(self, x):
        self.s += x

    def __str__(self):
        return self.s


class RedirectView(SmartView, AbstractUrlBasedView):

    URI_TEMPLATE_VARIABLE_PATTERN = re.compile("\\{([^/]+?)\\}")
    contextRelative: bool = False
    http10Compatible: bool = True
    exposeModelAttributes: bool = True
    encodingScheme: str = None
    statusCode: HttpStatus = None
    expandUriTemplateVariables: bool = True
    propagateQueryParams: bool = False
    hosts = list()

    def __init__(
        self,
        url: str = None,
        contextRelative: bool = False,
        http10Compatible: bool = True,
        exposeModelAttributes: bool = True,
    ):

        super().__init__(url)
        self.contextRelative = contextRelative
        self.http10Compatible = http10Compatible
        self.exposeModelAttributes = exposeModelAttributes
        self.set_expose_path_variables(False)

    def set_context_relative(self, contextRelative: bool) -> None:
        self.contextRelative = contextRelative

    def set_http_10_compatible(self, http10Compatible: bool) -> None:
        self.http10Compatible = http10Compatible

    def set_expose_model_attributes(self, exposeModelAttributes: bool) -> None:
        self.exposeModelAttributes = exposeModelAttributes

    def set_encoding_scheme(self, encodingScheme: str):
        self.encodingScheme = encodingScheme

    def set_status_code(self, statusCode: HttpStatus):
        self.statusCode = statusCode

    def set_expand_uri_template_variables(
        self, expandUriTemplateVariables: bool
    ) -> None:
        self.expandUriTemplateVariables = expandUriTemplateVariables

    def set_propagate_query_params(self, propagateQueryParams: bool) -> None:
        self.propagateQueryParams = propagateQueryParams

    def is_propagate_query_properties(self) -> bool:
        return self.propagateQueryParams

    def set_hosts(self, hosts: list) -> None:
        self.hosts = hosts

    def get_hosts(self) -> list:
        return self.hosts

    def is_redirect_view(self) -> bool:
        return True

    def is_context_required(self) -> bool:
        return False

    def render_merged_output_model(
        self, model: dict, request, response
    ) -> None:
        targetUrl: str = self.create_target_url(model, request)
        targetUrl = self.update_target_url(targetUrl, model, request, response)

        # Save flash attributes
        # TODO: RequestContextUtils
        # RequestContextUtils.saveOutputFlashMap(targetUrl, request, response)

        # Redirect
        self.send_redirect(request, response, targetUrl, self.http10Compatible)

    def create_target_url(self, model: dict, request) -> str:
        # TODO: StringBuilder
        targetUrl = StringBuilder()
        url: str = self.get_url()
        assert url is not None, "'url' not set"

        if self.contextRelative and self.get_url().startswith("/"):
            targetUrl.append(self.get_context_path(request))
        targetUrl.append(self.get_url())

        enc: str = self.encodingScheme
        if enc is None:
            enc = request.get_character_encoding()
        if enc is None:
            # TODO: WebUtils
            enc = WebUtils.DEFAULT_CHARACTER_ENCODING

        if self.expandUriTemplateVariables and targetUrl:
            variables: dict = self.get_current_request_uri_variables(request)
            targetUrl = self.replace_uri_template_variables(
                str(targetUrl), model, variables, enc
            )
        if self.is_propagate_query_properties():
            self.append_current_query_params(str(targetUrl), request)
        if self.exposeModelAttributes:
            self.append_query_properties(str(targetUrl), model, enc)
        return str(targetUrl)

    def get_context_path(self, request) -> str:
        contextPath: str = request.get_context_path()
        while contextPath.startswith("//"):
            contextPath = contextPath[1:]
        return contextPath

    def replace_uri_template_variables(
        self,
        targetUrl: str,
        model: dict,
        currentUriVariables: dict,
        encodingScheme: str,
    ):
        # TODO: StringBuilder
        result = StringBuilder()
        match = self.URI_TEMPLATE_VARIABLE_PATTERN.search(targetUrl)
        endLastMatch = 0
        if match:
            for g, name in enumerate(match.groups()):
                value = (
                    model.pop(name)
                    if name in model
                    else currentUriVariables.get(name)
                )
                if value is None:
                    raise Exception(f"Model has no value for key '{name}'")
                result.append(targetUrl[endLastMatch : match.start(g)])
                # result.append(UriUtils.encodePathSegment(str(value), encodingScheme))
                endLastMatch = match.end(g)
        result.append(targetUrl[endLastMatch:])
        return result

    def get_current_request_uri_variables(self, request) -> dict:
        # TODO
        name: str = HandlerMapping.URI_TEMPLATE_VARIABLES_ATTRIBUTE
        uriVars: dict = request.get_attribute(name)
        return {} if uriVars is None else uriVars

    def append_current_query_params(self, targetUrl: str, request) -> None:
        query: str = request.get_query_string()
        if query:
            fragment: str = None
            if "#" in targetUrl:
                anchorIndex = targetUrl.index("#")
                fragment = targetUrl[anchorIndex:]
                targetUrl = targetUrl[:anchorIndex]
            if "?" not in targetUrl:
                targetUrl = f"{targetUrl}?{query}"
            else:
                targetUrl = f"{targetUrl}&{query}"
            if fragment is not None:
                targetUrl += fragment

    def append_query_properties(
        self, targetUrl: str, model: dict, encodingScheme: str
    ) -> None:
        fragment: str = None
        if "#" in targetUrl:
            anchorIndex = targetUrl.index("#")
            fragment = targetUrl[anchorIndex:]
            targetUrl = targetUrl[:anchorIndex]

        first: bool = "?" in targetUrl
        for key, rawValue in self.query_properties(model).items():
            if rawValue is not None and hasattr(rawValue, "__iter__"):
                values = list(rawValue)
            else:
                values = [rawValue]
            for value in values:
                if first:
                    targetUrl += "?"
                    first = False
                else:
                    targetUrl += "&"
                encodedKey: str = self.url_encode(key, encodingScheme)
                encodedValue: str = (
                    ""
                    if value is None
                    else self.url_encode(str(value), encodingScheme)
                )
                targetUrl += f"{encodedKey}={encodedValue}"

        if fragment is not None:
            targetUrl += fragment

    def query_properties(self, model: dict) -> dict:
        result = {
            key: value
            for key, value in model.items()
            if self.is_eligible_property(key, value)
        }
        return result

    def is_eligible_property(self, key: str, value: object = None) -> bool:
        if value is None:
            return False
        if self.is_eligible_value(value):
            return True
        if hasattr(value, "__iter__"):
            if not value:
                return False
            for i in value:
                if not self.is_eligible_value(i):
                    return False
            return True
        return False

    def is_eligible_value(slef, value: object = None) -> bool:
        # TODO: BeanUtils
        return (value is not None) and (
            BeanUtils.isSimpleValueType(value.__class__)
        )

    def url_encode(self, input: str, encodingScheme: str) -> str:
        # TODO: URLEncoder
        return quote_plus(input, encoding=encodingScheme)

    def update_target_url(
        self, targetUrl: str, model: dict, request, response
    ):
        wac = self.get_web_application_context()
        # TODO: RequestContextUtils, RequestDataValueProcessor
        if wac is None:
            wac = RequestContextUtils.findWebApplicationContext(
                request, self.get_servlet_context()
            )
            # TODO: is mock ; just use None
            wac = None
        if (wac is not None) and wac.containsBean(
            RequestContextUtils.REQUEST_DATA_VALUE_PROCESSOR_BEAN_NAME
        ):
            processor = wac.getBean(
                RequestContextUtils.REQUEST_DATA_VALUE_PROCESSOR_BEAN_NAME,
                RequestDataValueProcessor,
            )
            return processor.processUrl(request, targetUrl)
        return targetUrl

    def send_redirect(
        self, request, response, targetUrl: str, http10Compatible: bool
    ):
        encodedURL: str = (
            targetUrl
            if self.is_remote_host(targetUrl)
            else response.encode_redirect_url(targetUrl)
        )
        if http10Compatible:
            attributeStatusCode: HttpStatus = request.get_attribute(
                View.RESPONSE_STATUS_ATTRIBUTE
            )
            if self.statusCode is not None:
                response.setStatus(self.statusCode.value())
                response.setHeader("Location", encodedURL)
            elif attributeStatusCode is not None:
                response.setStatus(attributeStatusCode.value())
                response.setHeader("Location", encodedURL)
            else:
                response.send_redirect(encodedURL)

        else:
            statusCode: HttpStatus = self.get_http_11_status_code(
                request, response, targetUrl
            )
            response.set_status(statusCode.value())
            response.set_header("Location", encodedURL)

    def is_remote_host(self, targetUrl: str) -> bool:
        if not self.get_hosts():
            return False
        # TODO: UriComponentsBuilder
        targetHost: str = (
            UriComponentsBuilder.fromUriString(targetUrl).build().getHost()
        )
        if not targetHost:
            return False
        for host in self.getHost():
            if targetHost == host:
                return False
        return True

    def get_http_11_status_code(
        self, request, response, targetUrl: str
    ) -> HttpStatus:
        if self.statusCode is not None:
            return self.statusCode
        attributeStatusCode: HttpStatus = request.get_attribute(
            View.RESPONSE_STATUS_ATTRIBUTE
        )
        if attributeStatusCode is not None:
            return attributeStatusCode
        tmp = HttpStatus.SEE_OTHER  # mock.MagicMock
        tmp.value.return_value = 303
        return tmp
