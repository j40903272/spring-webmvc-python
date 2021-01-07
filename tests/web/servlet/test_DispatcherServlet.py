from unittest import TestCase
from springframework.web.servlet.DispatcherServlet import DispatcherServlet
from springframework.web.testfixture.servlet.MockServletConfig import (
    MockServletConfig,
)
from springframework.web.testfixture.servlet.MockServletContext import (
    MockServletContext,
)
from springframework.web.testfixture.servlet.MockHttpServletRequest import (
    MockHttpServletRequest,
)
from springframework.web.testfixture.servlet.MockHttpServletResponse import (
    MockHttpServletResponse,
)


class TestDispatcherServlet(TestCase):
    def setUp(self):
        import os

        os.chdir(os.path.dirname(__file__))
        self.servletConfig = MockServletConfig(
            MockServletContext, servletName="simple"
        )
        self.dispatcherServlet = DispatcherServlet("./myservlet.xml")
        self.dispatcherServlet.init(self.servletConfig)

    def test_1(self):
        request = MockHttpServletRequest(
            self.servletConfig.get_servlet_context(),
            "GET",
            "/mycontext/myservlet/hello",
        )
        response = MockHttpServletResponse()

        request.set_context_path("/mycontext")
        request.set_servlet_path("/myservlet")
        request.set_path_info("/hello")
        request.set_query_string("?param1=value1")
        request.set_parameter("team id", [4])
        request.set_parameter("team member num", [6])

        self.dispatcherServlet.do_service(request, response)

    def test_2(self):
        request = MockHttpServletRequest(
            self.servletConfig.get_servlet_context(),
            "GET",
            "/mycontext/myservlet/welcome",
        )
        response = MockHttpServletResponse()

        request.set_context_path("/mycontext")
        request.set_servlet_path("/myservlet")
        request.set_path_info("/hello")
        request.set_query_string("?param1=value1")
        request.set_parameter("term project", "spring webmvc")

        self.dispatcherServlet.do_service(request, response)
