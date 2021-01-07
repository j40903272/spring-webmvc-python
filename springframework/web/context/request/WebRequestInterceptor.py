from abc import ABC


# dont use abstractmethod cause override is not neccessary
class WebRequestInterceptorInterface(ABC):
    def pre_handle(self, request, response, handler) -> bool:
        raise NotImplementedError

    def post_handle(self, request, response, handler, modelAndView) -> None:
        raise NotImplementedError

    def after_completion(self, request, response, handler, exception) -> None:
        raise NotImplementedError
