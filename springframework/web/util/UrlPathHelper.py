import logging
from springframework.utils.mock.inst import HttpServletRequest
from springframework.web.util.WebUtils import WebUtils


class UrlPathHelperMeta(type):
    def __init__(cls, *args, **kwargs):
        cls.PATH_ATTRIBUTE: str = cls.__name__ + ".path"


class UrlPathHelper(metaclass=UrlPathHelperMeta):
    def __init__(self):
        self.alwaysUseFullPath = False
        return

    def set_always_use_full_path(self, alwaysUseFullPath: bool):
        self.alwaysUseFullPath = alwaysUseFullPath

    def resolve_and_cache_lookup_path(
        self, request: HttpServletRequest
    ) -> str:
        lookupPath: str = self.get_lookup_path_for_request(request)
        logging.info(f"[lookupPath] = {lookupPath}")
        request.set_attribute(self.PATH_ATTRIBUTE, lookupPath)
        return lookupPath

    def get_lookup_path_for_request(self, request: HttpServletRequest) -> str:
        pathWithinApp: str = self.get_path_within_application(request)
        if self.alwaysUseFullPath:
            return pathWithinApp
        rest: str = self.get_path_within_servlet_mapping(
            request, pathWithinApp
        )
        if rest.replace(" ", ""):
            return rest
        else:
            return pathWithinApp

    def get_path_within_application(self, request: HttpServletRequest) -> str:
        contextPath: str = self.get_context_path(request)
        requestUri: str = self.get_request_uri(request)
        path: str = self.get_remaining_path(requestUri, contextPath, True)

        if path:
            # Normal case: URI contains context path.
            if path.replace(" ", "") == "":
                return "/"
            else:
                return path
        else:
            return requestUri

    def get_path_within_servlet_mapping(
        self, request: HttpServletRequest, pathWithinApp: str
    ) -> str:
        servletPath: str = request.get_servlet_path()
        sanitizedPathWithinApp: str = self.get_sanitized_path(pathWithinApp)
        path: str = ""
        if sanitizedPathWithinApp in servletPath:
            path = self.get_remaining_path(
                sanitizedPathWithinApp, servletPath, False
            )
        else:
            path = self.get_remaining_path(pathWithinApp, servletPath, False)
        if path:
            return path
        else:
            return request.get_path_info()

    def get_context_path(self, request: HttpServletRequest) -> str:
        contextPath: str = request.get_attribute(
            WebUtils.INCLUDE_SERVLET_PATH_ATTRIBUTE
        )
        if not contextPath:
            contextPath = request.get_context_path()
        if contextPath == "/":
            contextPath = ""
        return self.decode_request_string(request, contextPath)

    def get_request_uri(self, request: HttpServletRequest) -> str:
        uri: str = request.get_attribute(
            WebUtils.INCLUDE_REQUEST_URI_ATTRIBUTE
        )
        if not uri:
            uri = request.get_request_uri()
        return self.decode_and_clean_uri_string(request, uri)

    def decode_request_string(
        self, request: HttpServletRequest, source: str
    ) -> str:
        # Ignore decode
        return source

    def decode_and_clean_uri_string(
        self, request: HttpServletRequest, uri: str
    ) -> str:
        uri = self.remove_semicolon_content(uri)
        uri = self.decode_request_string(request, uri)
        uri = self.get_sanitized_path(uri)
        return uri

    def remove_semicolon_content(self, requestUri: str) -> str:
        if not requestUri:
            return ""
        res: str = ""
        state = False
        for i in requestUri:
            if i == ";":
                state = True
            if state == False:
                res = res + i
            if i == "/":
                state = False
        return res

    def get_sanitized_path(self, path: str) -> str:
        return path.replace("//", "/")

    def get_remaining_path(
        self, requestUri: str, mapping: str, ignoreCase: bool
    ) -> str:
        index1: int = 0
        index2: int = 0
        while index1 < len(requestUri) and index2 < len(mapping):
            c1: str = requestUri[index1]
            c2: str = mapping[index2]
            if c1 == ",":
                index = requestUri.index("/", index1)
                if index == -1:
                    return None
                c1 = requestUri[index1]
            if c1 == c2 or (ignoreCase and c1.lower() == c2.lower()):
                index1 += 1
                index2 += 1
                continue
            return None

        if index2 != len(mapping):
            return None
        elif index1 == len(requestUri):
            return ""
        elif requestUri[index1] == ";":
            index = requestUri.index("/", index1)
        return requestUri[index1:] if index1 != -1 else ""
