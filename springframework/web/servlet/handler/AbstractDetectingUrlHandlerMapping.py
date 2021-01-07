import logging
from abc import ABC, abstractmethod

from springframework.web.servlet.handler.AbstractUrlHandlerMapping import (
    AbstractUrlHandlerMapping,
)
from springframework.utils.mock.inst import BeanFactoryUtils


class AbstractDetectingUrlHandlerMapping(AbstractUrlHandlerMapping, ABC):

    detectHandlersInAncestorContexts: bool = False

    def setDetectHandlersInAncestorContexts(
        self, detectHandlersInAncestorContexts: bool
    ) -> None:
        self.detectHandlersInAncestorContexts = (
            detectHandlersInAncestorContexts
        )

    def initApplicationContext(self) -> None:
        super().initApplicationContext()
        self.detectHandlers()

    def detectHandlers(self) -> None:
        applicationContext = self.obtainApplicationContext()
        beanNames = list()
        if self.detectHandlersInAncestorContexts:
            beanNames = BeanFactoryUtils.beanNamesForTypeIncludingAncestors(
                applicationContext, object
            )
        else:
            beanNames = applicationContext.getBeanNamesForType(object)

        for beanName in beanNames:
            urls: list = self.determineUrlsForHandler(beanName)
            if urls:
                self.registerHandler(urls, beanName)

        # TODO
        if not self.getHandlerMap().isEmpty():
            logging.debug(
                f"Detected {self.getHandlerMap().size()} mappings in {self.formatMappingName()}"
            )

    @abstractmethod
    def determineUrlsForHandler(self, beanName: str) -> list:
        raise NotImplementedError
