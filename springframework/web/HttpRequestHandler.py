from abc import ABC, abstractmethod
from springframework.utils.mock.type import HttpServletRequest
from springframework.utils.mock.type import HttpServletResponse


class HttpRequestHandler(ABC):
    @abstractmethod
    def handleRequest(
        self, request: "HttpServletRequest", response: "HttpServletResponse"
    ) -> None:
        pass
