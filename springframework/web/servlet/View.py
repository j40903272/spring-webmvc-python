from abc import ABC, abstractmethod


class View(ABC):
    RESPONSE_STATUS_ATTRIBUTE = "View" + ".responseStatus"
    PATH_VARIABLES = "View" + ".pathVariables"
    SELECTED_CONTENT_TYPE = "View" + ".selectedContentType"

    def __init__(self):
        View.RESPONSE_STATUS_ATTRIBUTE = (
            self.__class__.__name__ + ".responseStatus"
        )
        View.PATH_VARIABLES = self.__class__.__name__ + ".pathVariables"
        View.SELECTED_CONTENT_TYPE = (
            self.__class__.__name__ + ".selectedContentType"
        )

    def get_content_type(self):
        return None

    @abstractmethod
    def render(self, request, response, model=None):
        raise NotImplementedError
