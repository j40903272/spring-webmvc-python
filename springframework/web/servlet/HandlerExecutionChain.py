import logging
from springframework.utils.mock.type import AsyncHandlerInterceptor


class HandlerExecutionChain:
    def __init__(self, handler: object, interceptors: list = []):
        self.logger = logging.getLogger(__name__)
        self.interceptorIndex = -1
        self.interceptorList = []

        if isinstance(handler, HandlerExecutionChain):
            originalChain = handler
            self.interceptorList.extend(originalChain.interceptorList)
        else:
            self.handler = handler
        self.interceptorList.extend(interceptors)

    def get_handler(self) -> object:
        return self.handler

    def add_interceptor(self, index: int, interceptor=None) -> None:
        if isinstance(index, int) and interceptor is not None:
            self.interceptorList.insert(index, interceptor)
        elif interceptor is None and isinstance(index, object):
            interceptor = index
            self.interceptorList.append(interceptor)

    def add_interceptors(self, interceptors: list) -> None:
        self.interceptorList.extend(interceptors)

    def get_interceptors(self) -> list:
        return self.interceptorList

    def get_interceptor_list(self) -> list:
        return self.interceptorList

    def apply_pre_handle(self, request, response) -> bool:
        for e, interceptor in enumerate(self.interceptorList):
            if not interceptor.pre_handle(request, response, self.handler):
                self.trigger_after_completion(request, response, None)
            self.interceptorIndex = e
        return True

    def apply_post_handle(self, request, response, mv=None) -> None:
        for interceptor in self.interceptorList[::-1]:
            interceptor.post_handle(request, response, self.handler, mv)

    def trigger_after_completion(self, request, response, ex) -> None:
        for interceptor in self.interceptorList[: self.interceptorIndex][::-1]:
            try:
                interceptor.after_completion(
                    request, response, self.handler, ex
                )
            except Exception as ex2:
                self.logger.error(
                    "HandlerInterceptor.afterCompletion threw exception", ex2
                )

    def apply_after_concurrent_handling_started(
        self, request, response
    ) -> None:
        for e, interceptor in enumerate(self.interceptorList):
            if isinstance(interceptor, AsyncHandlerInterceptor):
                try:
                    asyncInterceptor = interceptor
                    asyncInterceptor.afterConcurrentHandlingStarted(
                        request, response, self.handler
                    )
                except Exception as ex:
                    self.logger.error(
                        f"Interceptor [{interceptor}] failed in afterConcurrentHandlingStarted. {ex}"
                    )

    def __str__(self):
        return f"HandlerExecutionChain with [{self.get_handler()}] and {len(self.interceptorList)} interceptors"
