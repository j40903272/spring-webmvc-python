from unittest import TestCase
from springframework.web.servlet.handler import SimpleUrlHandlerMapping
from springframework.web.servlet import HandlerExecutionChain, HandlerMapping
from springframework.web.testfixture.servlet import (
    MockHttpServletRequest as HttpServletRequest,
)
from springframework.web.testfixture.servlet import (
    MockHttpServletResponse as HttpServletResponse,
)


class MockController:
    def __init__(self, name: str):
        self.name = name

    def get_name(self) -> str:
        return self.name


class MockSimpleUrlHandlerMapping(SimpleUrlHandlerMapping):
    def __init__(self, urlMap: dict(), mockLookupPath: str):
        super().__init__(urlMap)
        self.mockLookupPath = mockLookupPath

    def init_lookup_path(self, request):
        return self.mockLookupPath


class TestSimpleURLHandlerMapping(TestCase):
    def setUp(self):
        self.urlMap = {
            "/": MockController("/"),
            "test": MockController("test"),
        }
        self.request = HttpServletRequest(
            servletContext="Context",
            method="GET",
            requestURI="/mycontext/myservlet/test",
        )
        self.request.set_context_path("/mycontext")
        self.request.set_servlet_path("/myservlet")
        self.request.set_path_info("/test")
        self.request.set_query_string("?param1=value1")
        self.response = HttpServletResponse()

    def test_init_lookup_path(self):
        handlerMapping: HandlerMapping = SimpleUrlHandlerMapping(self.urlMap)
        handlerMapping.init_lookup_path(self.request)

    def test_register_handlers(self):
        handlerMapping: HandlerMapping = SimpleUrlHandlerMapping(self.urlMap)
        handlerMapping.init_application_context()

    def test_mapping_directly(self):
        handlerMapping: HandlerMapping = SimpleUrlHandlerMapping(self.urlMap)
        handlerMapping.init_application_context()
        mappedHandler: HandlerExecutionChain = handlerMapping.get_handler(
            self.request
        )
        ha = mappedHandler.get_handler()
        mappedHandler.apply_post_handle(self.request, self.response, None)

    def test_end_to_end(self):
        handlerMapping: HandlerMapping = SimpleUrlHandlerMapping(self.urlMap)
        handlerMapping.init_application_context()
        mappedHandler: HandlerExecutionChain = handlerMapping.get_handler(
            self.request
        )
