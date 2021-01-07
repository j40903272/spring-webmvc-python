from unittest import mock
import logging
from abc import abstractmethod, ABC

from springframework.web.context.support.WebApplicationObjectSupport import (
    WebApplicationObjectSupport,
)
from springframework.beans.factory.BeanNameAware import BeanNameAware
from springframework.web.servlet.View import View

# mock objects
RequestContext = mock.MagicMock()
RequestContext.configure_mock(name="RequestContext")
ContextExposingHttpServletRequest = mock.MagicMock()
ContextExposingHttpServletRequest.configure_mock(
    name="ContextExposingHttpServletRequest"
)
mediaType = mock.MagicMock()
mediaType.configure_mock(name="mediaType")


class AbstractView(WebApplicationObjectSupport, View, BeanNameAware, ABC):
    DEFAULT_CONTENT_TYPE = "text/html;charset=ISO-8859-1"
    OUTPUT_BYTE_ARRAY_INITIAL_SIZE = 4096
    contentType = DEFAULT_CONTENT_TYPE

    def __init__(self):
        super().__init__()
        self.staticAttributes = dict()
        self.exposedContextBeanNames = set()
        self.requestContextAttribute: str = None
        self.exposePathVariables = True
        self.exposeContextBeansAsAttributes = False
        self.beanName: str = None

    def set_content_type(self, contentType: str = None) -> None:
        self.contentType = contentType

    def get_content_type(self) -> str:
        return self.contentType

    def set_request_context_attribute(
        self, requestContextAttribute: str
    ) -> None:
        self.requestContextAttribute = requestContextAttribute

    def get_request_context_attribute(self) -> str:
        return self.requestContextAttribute

    def set_attributes_csv(self, propString: str = None) -> None:
        if propString is not None:
            token_list = propString.split(",")
            for token in token_list:
                if not token:
                    continue
                if "=" not in token:
                    raise ValueError(
                        "Expected '=' in attributes CSV string '"
                        + propString
                        + "'"
                    )
                if token.index("=") >= (len(token) - 2):
                    raise ValueError(
                        "At least 2 characters ([]) required in attributes CSV string '"
                        + propString
                        + "'"
                    )
                name, value = token.split("=")
                value = value[1:-1]
                self.add_static_attribute(name, value)

    def set_attributes(self, attributes: dict) -> None:
        if attributes is not None:
            self.staticAttributes.update(attributes)

    def set_attributes_map(self, attributes: dict = None) -> None:
        if attributes is not None:
            for name in attributes:
                value = attributes[name]
                self.add_static_attribute(name, value)

    def get_attributes_map(self) -> dict:
        return self.staticAttributes

    def add_static_attribute(self, name: str, value) -> None:
        self.staticAttributes[name] = value

    def get_static_attributes(self) -> dict:
        return self.staticAttributes.copy()

    def set_expose_path_variables(self, exposePathVariables: bool) -> None:
        self.exposePathVariables = exposePathVariables

    def is_expose_path_variables(self) -> bool:
        return self.exposePathVariables

    def set_expose_context_beans_as_attributes(
        self, exposeContextBeansAsAttributes: bool
    ) -> None:
        self.exposeContextBeansAsAttributes = exposeContextBeansAsAttributes

    def set_exposed_context_bean_names(
        self, exposedContextBeanNames: list
    ) -> None:
        self.exposedContextBeanNames = set(exposedContextBeanNames)

    def set_bean_name(self, beanName: str) -> None:
        self.beanName = beanName

    def get_bean_name(self) -> str:
        return self.beanName

    def render(self, model, request, response) -> None:
        logging.info(
            "View "
            + self.format_view_name()
            + ", model "
            + str((dict() if model is None else model))
            + f", static attributes {self.staticAttributes if self.staticAttributes else ''}"
        )
        mergedModel = self.create_merged_output_model(model, request, response)
        self.prepare_response(request, response)
        self.render_merged_output_model(
            mergedModel, self.get_request_to_expose(request), response
        )

    def create_merged_output_model(
        self, model: dict, request, response
    ) -> dict:
        pathVars = None
        if self.exposePathVariables:
            pathVars = request.get_attribute(View.PATH_VARIABLES)

        size = len(self.staticAttributes)
        size += 0 if model is None else len(model)
        size += 0 if pathVars is None else len(pathVars)

        mergedModel = dict()
        mergedModel.update(self.staticAttributes)
        if pathVars is not None:
            mergedModel.update(pathVars)
        if model is not None:
            mergedModel.update(model)

        # Expose RequestContext?
        if self.requestContextAttribute is not None:
            value = self.create_request_context(request, response, mergedModel)
            mergedModel[self.requestContextAttribute] = value

        return mergedModel

    def create_request_context(
        self, request, response, model: dict
    ) -> RequestContext:
        # RequestContext use mock
        return RequestContext(
            request, response, self.get_servlet_context(), model
        )

    def prepare_response(self, request, response) -> None:
        if self.generates_download_content():
            response.setHeader("Pragma", "private")
            response.setHeader("Cache-Control", "private, must-revalidate")

    def generates_download_content(self) -> bool:
        return False

    # return type : HttpServletRequest
    def get_request_to_expose(self, originalRequest):
        if self.exposeContextBeansAsAttributes or self.exposedContextBeanNames:
            # wac = getWebApplicationContext()
            wac = self.get_web_application_context()
            assert wac is None, "No WebApplicationContext"
            # ContextExposingHttpServletRequest use mock
            return ContextExposingHttpServletRequest(
                originalRequest, wac, self.exposedContextBeanNames
            )
        return originalRequest

    @abstractmethod
    def render_merged_output_model(self, model: dict, request, response):
        raise NotImplementedError

    def expose_model_as_request_attributes(self, model: dict, request):
        for name, value in model.items():
            # make sure request has this method
            if value is not None:
                request.set_attribute(name, value)
            else:
                request.remove_attribute(name)

    def create_temporary_output_stream(self) -> bytearray:
        return bytearray(self.OUTPUT_BYTE_ARRAY_INITIAL_SIZE)

    def write_to_response(self, response, baos: bytearray):
        # Write content type and also length (determined via byte array).
        response.set_content_type(self.get_content_type())
        response.setContentLength(len(baos))

        # Flush byte array to servlet output stream.
        out = response.getOutputStream()
        baos.writeTo(out)
        out.flush()

    def set_response_content_type(self, request, response) -> None:
        # mediaType use mock
        mediaType = request.getattr(View.SELECTED_CONTENT_TYPE)
        if mediaType is not None and mediaType.isConcrete():
            response.set_content_type(mediaType.toString())
        else:
            response.set_content_type(self.get_content_type())

    def __str__(self) -> str:
        return self.__class__.__qualname__ + ": " + self.format_view_name()

    def format_view_name(self) -> str:
        if self.get_bean_name() is not None:
            return "name '" + self.get_bean_name() + "'"
        else:
            return "[" + self.__class__.__name__ + "]"
