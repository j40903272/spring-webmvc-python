import threading
from unittest import mock
from springframework.utils.mock.inst import AsyncEvent
from springframework.web.testfixture.servlet.MockHttpServletRequest import (
    MockHttpServletRequest,
)
from springframework.web.testfixture.servlet.MockHttpServletResponse import (
    MockHttpServletResponse,
)


class MockAsyncContext:

    request = None
    response = None
    listeners = list()
    dispatchedPath: str = None
    timeout: int = 10000
    dispatchHandlers = list()

    def __init__(self, request, response=None):
        self.request = request
        self.response = response

    def addDispatchHandler(self, handler) -> None:
        assert handler is not None, "Dispatch handler must not be null"
        with threading.Lock():
            if self.dispatchedPath is None:
                self.dispatchHandlers.append(handler)
            else:
                handler.run()

    def getRequest(self):
        return self.request

    def getResponse(self):
        return self.response

    def hasOriginalRequestAndResponse(self) -> bool:
        return isinstance(self.request, MockHttpServletRequest) and isinstance(
            self.response, MockHttpServletResponse
        )

    def dispatch(self, context, path: str) -> None:
        with threading.Lock():
            self.dispatchedPath = path
            for handler in self.dispatchHandlers:
                handler.run()

    def getDispatchedPath(self) -> str:
        return self.dispatchedPath

    def complete(self) -> None:
        mockRequest = MockHttpServletRequest(self.request)
        if mockRequest is not None:
            mockRequest.setAsyncStarted(False)
        for listener in self.listeners:
            try:
                listener.onComplete(
                    AsyncEvent(self, self.request, self.response)
                )
            except Exception as e:
                raise ValueError(f"AsyncListener failure. {e}")

    def start(self, runnable) -> None:
        runnable.run()

    def addListener(self, listener):
        self.listeners.append(listener)

    def getListeners(self) -> list:
        return self.listeners

    def createListener(self, clazz):
        # TODO
        return mock.MagicMock(spec=clazz)
        # return BeanUtils.instantiateClass(clazz)

    def setTimeout(self, timeout) -> None:
        self.timeout = timeout

    def getTimeout(self) -> None:
        return self.timeout
