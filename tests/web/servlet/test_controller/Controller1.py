from springframework.web.servlet.ModelAndView import ModelAndView
from springframework.web.servlet.mvc.Controller import Controller

# from springframework.utils.mock.inst import HttpServletResponse, HttpServletRequest
# from springframework.web.servlet.view import InternalResourceView
from springframework.web.testfixture.servlet import (
    MockHttpServletRequest,
    MockHttpServletResponse,
)


class Controller1(Controller):
    def handle_request(
        self,
        request: MockHttpServletRequest,
        response: MockHttpServletResponse,
    ):
        print("Controller1 invoked!!!")
        mav = ModelAndView()
        # internalResourceView = InternalResourceView(request.get_request_url())
        # mav.set_view(internalResourceView)
        names = request.get_parameter_names()
        values = request.get_parameter_values()
        assert len(names) == len(values)
        mav.set_view_name("hello")
        for name, value in zip(names, values):
            mav.add_object(name, value)
        return mav
