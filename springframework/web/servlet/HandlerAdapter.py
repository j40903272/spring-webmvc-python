from abc import ABC, abstractmethod

from springframework.utils.mock.inst import (
    HttpServletResponse,
    HttpServletRequest,
)
from springframework.web.servlet.ModelAndView import ModelAndView


class HandlerAdapter(ABC):
    @abstractmethod
    def supports(self, handler) -> bool:
        raise NotImplementedError

    @abstractmethod
    def handle(
        self,
        request: HttpServletRequest,
        response: HttpServletResponse,
        handler,
    ) -> ModelAndView:
        raise NotImplementedError

    @abstractmethod
    def get_last_modified(self, request: HttpServletRequest, handler) -> int:
        raise NotImplementedError
