from springframework.web.servlet import (
    HandlerAdapter as HandlerAdapterInterface,
)
from springframework.web.servlet import ModelAndView
from springframework.utils.mock.type import Servlet


class SimpleServletHandlerAdapter(HandlerAdapterInterface):
    def supports(self, handler: object) -> bool:
        return isinstance(handler, Servlet)

    def handle(self, request, response, handler: object) -> ModelAndView:
        handler.service(request, response)
        return None

    def get_last_modified(self, request, handle: object) -> int:
        return -1
