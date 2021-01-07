from abc import ABC, abstractmethod
from springframework.web.servlet import View
from springframework.utils.mock.inst import Locale


class ViewResolver(ABC):
    @abstractmethod
    def resolve_view_name(self, viewName: str, locale: Locale) -> View:
        raise NotImplementedError
