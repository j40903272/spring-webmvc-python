from unittest import TestCase
from springframework.web.servlet import View
from springframework.web.testfixture.servlet import (
    MockHttpServletRequest as HttpServletRequest,
)
from springframework.web.testfixture.servlet import (
    MockHttpServletResponse as HttpServletResponse,
)
from springframework.web.testfixture.servlet import (
    MockServletContext,
    MockRequestDispatcher,
)
from springframework.web.servlet.view import InternalResourceView
from springframework.web.util.WebUtils import WebUtils


class TestInternalResourceView(TestCase):
    def setUp(self) -> None:
        self.model = {"foo": "bar", "I": 1}
        self.url = "forward-to"
        self.request = HttpServletRequest()
        self.response = HttpServletResponse()
        self.view = InternalResourceView()

    def test_set_always_include(self):
        with self.assertRaises(ValueError):
            self.view.after_properties_set()
        # self.fail()

    def test_render_merged_output_model(self):
        self.skipTest("TODO")
        # self.fail()

    def test_use_include(self):
        self.skipTest("TODO")
        # self.fail()

    ###########
    # DADA ADD
    ###########

    def test_reject_null_url(self):
        with self.assertRaises(Exception):
            self.view.after_properties_set()

    def test_forward(self):
        request = HttpServletRequest("GET", "/myservlet/handler.do")
        request.set_context_path("/mycontext")
        request.set_servlet_path("/myservlet")
        request.set_path_info(";mypathinfo")
        request.set_query_string("?param1=value1")

        self.view.set_url(self.url)
        tmp = MockServletContext()
        tmp.minorVersion = 4
        self.view.set_servlet_context(tmp)

        self.view.render(self.model, request, self.response)
        self.assertEqual(self.response.get_forwarded_url(), self.url)
        for key, value in self.model.items():
            msg = f"Values for model key '{key}' must match"
            self.assertEqual(request.get_attribute(key), value, msg=msg)

    def test_always_include(self):
        self.assertIsNone(self.request.get_attribute(View.PATH_VARIABLES))
        # DADA modify to compare resource :)
        self.assertEqual(
            self.request.get_request_dispatcher(self.url).resource,
            MockRequestDispatcher(self.url).resource,
        )

        self.view.set_url(self.url)
        self.view.set_always_include(True)

        # Can now try multiple tests
        self.view.render(self.model, self.request, self.response)
        self.assertEqual(self.response.get_included_url(), self.url)
        for key, value in self.model.items():
            self.request.set_attribute(key, value)

    def test_include_attribute(self):
        self.response = HttpServletResponse()
        self.assertIsNone(self.request.get_attribute(View.PATH_VARIABLES))
        self.assertIsNone(
            self.request.get_attribute(WebUtils.INCLUDE_REQUEST_URI_ATTRIBUTE)
        )
        # DADA modify to compare resource :)
        self.assertEqual(
            self.request.get_request_dispatcher(self.url).resource,
            MockRequestDispatcher(self.url).resource,
        )

        self.response.set_committed(True)
        self.view.set_url(self.url)
        import logging

        logging.error(self.response.includedUrls)

        # Can now try multiple tests
        self.view.render(self.model, self.request, self.response)
        self.assertEqual(self.response.get_included_url(), self.url)
        for key, value in self.model.items():
            self.request.set_attribute(key, value)
