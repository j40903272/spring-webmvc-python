from unittest import TestCase, mock
from springframework.web.context.support.WebApplicationContext import (
    WebApplicationContext,
)
from springframework.web.testfixture.servlet import MockServletContext
from springframework.web.testfixture.servlet import MockHttpServletRequest
from springframework.web.testfixture.servlet import MockHttpServletResponse
from springframework.web.servlet import View
from springframework.web.servlet.view import AbstractView


class TestView(TestCase):
    def setUp(self):
        pass

    def test_render_without_static_attributes(self):
        wac = mock.MagicMock(spec=WebApplicationContext)
        wac.get_servlet_context.return_value = MockServletContext()
        # self.assertEqual(wac.get_servlet_context(), MockServletContext())

        request = MockHttpServletRequest()
        response = MockHttpServletResponse()
        view = testView(wac)

        # Check superclass handles duplicate init
        view.set_application_context(wac)
        view.set_application_context(wac)

        model = {"foo": "bar", "something": object()}
        view.render(model, request, response)
        self.assertEqual(dict(view.model, **model), view.model)
        self.assertTrue(view.initialized)

    def test_render_with_static_attributes_no_collision(self):
        wac = mock.MagicMock(spec=WebApplicationContext)
        wac.get_servlet_context.return_value = MockServletContext()

        request = MockHttpServletRequest()
        response = MockHttpServletResponse()
        view = testView(wac)
        view.set_application_context(wac)

        properties = {"foo": "bar", "something": "else"}
        view.set_attributes(properties)
        model = {"one": {}, "two": object()}
        view.render(model, request, response)

        self.assertEqual(dict(view.model, **model), view.model)
        self.assertEqual(dict(view.model, **properties), view.model)
        self.assertTrue(view.initialized)

    def test_path_vars_override_static_attributes(self):
        wac = mock.MagicMock(spec=WebApplicationContext)
        wac.get_servlet_context.return_value = MockServletContext()

        request = MockHttpServletRequest()
        response = MockHttpServletResponse()
        view = testView(wac)
        view.set_application_context(wac)

        properties = {"one": "bar", "something": "else"}
        view.set_attributes(properties)
        pathVars = {"one": {}, "two": object()}
        request.set_attribute(View.PATH_VARIABLES, pathVars)

        view.render({}, request, response)

        self.assertEqual(dict(view.model, **pathVars), view.model)
        self.assertEqual(len(view.model), 3)
        self.assertEqual(view.model.get("something"), "else")
        self.assertTrue(view.initialized)

    def test_dynamic_model_overrides_static_attributes_if_collision(self):
        wac = mock.MagicMock(spec=WebApplicationContext)
        wac.get_servlet_context.return_value = MockServletContext()

        request = MockHttpServletRequest()
        response = MockHttpServletResponse()
        view = testView(wac)
        view.set_application_context(wac)

        properties = {"one": "bar", "something": "else"}
        view.set_attributes(properties)
        model = {"one": {}, "two": object()}
        view.render(model, request, response)

        self.assertEqual(len(view.model), 3)
        self.assertEqual(view.model.get("something"), "else")
        self.assertTrue(view.initialized)

    def test_dynamic_model_overrides_path_variables(self):
        wac = mock.MagicMock(spec=WebApplicationContext)
        wac.get_servlet_context.return_value = MockServletContext()

        request = MockHttpServletRequest()
        response = MockHttpServletResponse()
        view = testView(wac)
        view.set_application_context(wac)

        pathVars = {"one": "bar", "something": "else"}
        request.set_attribute(View.PATH_VARIABLES, pathVars)
        model = {"one": {}, "two": object()}
        view.render(model, request, response)

        self.assertEqual(dict(view.model, **model), view.model)
        self.assertEqual(len(view.model), 3)
        self.assertEqual(view.model.get("something"), "else")
        self.assertTrue(view.initialized)

    def test_ignores_null_attributes(self):
        view = ConcreteView()
        view.set_attributes(None)
        self.assertEqual(len(view.get_static_attributes()), 0)

    def test_attribute_csv_parsing_ignores_null(self):
        view = ConcreteView()
        view.set_attributes_csv(None)
        self.assertEqual(len(view.get_static_attributes()), 0)

    def test_attribute_csv_parsing_valid(self):
        view = ConcreteView()
        view.set_attributes_csv("foo=[bar],king=[kong]")
        self.assertEqual(len(view.get_static_attributes()), 2)
        self.assertEqual(view.get_static_attributes().get("foo"), "bar")
        self.assertEqual(view.get_static_attributes().get("king"), "kong")

    def test_attribute_csv_parsing_valid_with_weird_characters(self):
        view = ConcreteView()
        fooval = "owfie   fue&3[][[[2 \n\n \r  \t 8\ufffd3"
        # also test empty value
        kingval = ""
        view.set_attributes_csv(f"foo=({fooval}),king={{{kingval}}},f1=[we]")
        self.assertEqual(len(view.get_static_attributes()), 3)
        self.assertEqual(view.get_static_attributes().get("foo"), fooval)
        self.assertEqual(view.get_static_attributes().get("king"), kingval)

    def test_attribute_csv_parsing_ignore_trailing_comma(self):
        view = ConcreteView()
        view.set_attributes_csv("foo=[de],")
        self.assertEqual(len(view.get_static_attributes()), 1)


class ConcreteView(AbstractView):
    def render_merged_output_model(self, model, request, response):
        raise Exception("UnsupportedOperationException")


class testView(AbstractView):
    def __init__(self, wac=None):
        super().__init__()
        self.wac = wac

    def render_merged_output_model(self, model: dict, request, response):
        self.model = model

    # override original function and become overloading
    # so must add second argument
    def init_application_context(self, context=None):
        self.initialized = True
        assert self.wac == self.get_application_context()
