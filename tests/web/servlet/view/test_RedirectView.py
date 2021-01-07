from unittest import TestCase, mock
from springframework.web.servlet.view import RedirectView
from springframework.web.testfixture.servlet import MockHttpServletRequest
from springframework.web.testfixture.servlet import MockHttpServletResponse
from springframework.web.util.WebUtils import WebUtils
from springframework.web.servlet.DispatcherServlet import DispatcherServlet


class TestRedirectView(TestCase):
    def setUp(self):
        self.request = MockHttpServletRequest()
        self.request.set_context_path("/context")
        self.request.set_character_encoding(
            WebUtils.DEFAULT_CHARACTER_ENCODING
        )
        self.request.set_attribute(
            DispatcherServlet.OUTPUT_FLASH_MAP_ATTRIBUTE,
            mock.MagicMock(name="FlashMap"),
        )
        self.request.set_attribute(
            DispatcherServlet.FLASH_MAP_MANAGER_ATTRIBUTE,
            mock.MagicMock(name="SessionFlashMapManager"),
        )
        self.response = MockHttpServletResponse()

    def test_no_url_set(self):
        view = RedirectView()
        with self.assertRaises(Exception):
            view.after_properties_set()

    def test_http11(self):
        view = RedirectView()
        view.set_url("https://url.somewhere.com")
        view.set_http_10_compatible(False)
        view.render({}, self.request, self.response)
        self.assertEqual(self.response.get_status(), 303)
        self.assertEqual(
            self.response.get_header("Location"), "https://url.somewhere.com"
        )
