from abc import ABC

# from springframework.web.method import HandlerMethod


# dont use abstractmethod cause override is not neccessary
class HandlerInterceptorInterface(ABC):
    def pre_handle(self, request, response, handler) -> bool:
        pass

    def post_handle(self, request, response, handler, modelAndView) -> None:
        pass

    def after_completion(self, request, response, handler, exception) -> None:
        pass
