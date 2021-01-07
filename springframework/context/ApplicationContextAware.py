from abc import abstractmethod

from springframework.context.ApplicationContext import ApplicationContext
from springframework.beans.factory.Aware import Aware


class ApplicationContextAware(Aware):
    @abstractmethod
    def set_application_context(self, application_context: ApplicationContext):
        raise NotImplementedError
