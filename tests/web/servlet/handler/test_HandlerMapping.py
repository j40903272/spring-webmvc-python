from unittest import TestCase, mock
from springframework.web.servlet.handler import AbstractHandlerMapping
from springframework.web.servlet.HandlerInterceptor import (
    HandlerInterceptorInterface as HandlerInterceptor,
)
from springframework.web.context.support.StaticWebApplicationContext import (
    StaticWebApplicationContext,
)


class TestHandlerMapping(TestCase):
    def setUp(self):
        pass

    def test_ordered_interceptors(self):
        i1 = mock.MagicMock(spec=HandlerInterceptor)
        i2 = mock.MagicMock(spec=HandlerInterceptor)
        i3 = mock.MagicMock(spec=HandlerInterceptor)
        i4 = mock.MagicMock(spec=HandlerInterceptor)
        i1.includePatterns = ["/**"]
        i3.includePatterns = ["/**"]

        mapping = MockHandlerMapping()
        mapping.set_application_context(StaticWebApplicationContext())

        requestFactory = mock.MagicMock(name="requestFactory")
        requestFactory.apply("/")
        chain = mapping.get_handler(requestFactory)


class MockHandlerMapping(AbstractHandlerMapping):
    def getHandlerInternal(self, request):
        self.init_lookup_path(request)
        return object()

    def get_handler_internal(self, *args):
        pass
