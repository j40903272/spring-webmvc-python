from springframework.beans.factory.Aware import Aware
from abc import ABC, abstractmethod
from springframework.utils.mock.inst import ServletContext


class ServletContextAware(Aware, ABC):
    @abstractmethod
    def set_servlet_context(self, servlet_context: ServletContext):
        raise NotImplementedError
