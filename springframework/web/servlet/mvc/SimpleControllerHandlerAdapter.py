from springframework.web.servlet import ModelAndView
from springframework.web.servlet.HandlerAdapter import HandlerAdapter
from springframework.web.servlet.mvc.Controller import Controller
from springframework.web.servlet.mvc.LastModified import LastModified
from springframework.utils.mock.inst import (
    HttpServletResponse,
    HttpServletRequest,
)


class SimpleControllerHandlerAdapter(HandlerAdapter):
    def supports(self, handler: object) -> bool:
        return isinstance(handler, Controller)

    def handle(
        self,
        request: HttpServletRequest,
        response: HttpServletResponse,
        handler: object,
    ) -> ModelAndView:
        handler: Controller = handler
        return handler.handle_request(request, response)

    def get_last_modified(
        self, request: HttpServletRequest, handler: object
    ) -> int:
        if isinstance(handler, LastModified):
            handler: Controller = handler
            return handler.get_last_modified(request)
        return -1
