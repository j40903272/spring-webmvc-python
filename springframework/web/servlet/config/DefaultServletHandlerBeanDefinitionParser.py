from unittest import mock
from springframework.beans.factory.config import BeanDefinitionInterface
from springframework.beans.factory.xml import (
    BeanDefinitionParser,
    ParserContext,
)
from xml.etree.ElementTree import Element
from .MvcNamespaceUtils import registerDefaultComponents


class DefaultServletHandlerBeanDefinitionParser(BeanDefinitionParser):
    def parse(
        self, element: Element, parserContext: ParserContext
    ) -> BeanDefinitionInterface:
        source = parserContext.extractSource(element)

        defaultServletName: str = element.getattr("default-servlet-name", None)
        # RootBeanDefinition use mock
        RootBeanDefinition = mock.MagicMock()
        mock.configure_mock(name="RootBeanDefinition")
        defaultServletHandlerDef = RootBeanDefinition()
        defaultServletHandlerDef.setSource(source)
        defaultServletHandlerDef.setRole(
            BeanDefinitionInterface.ROLE_INFRASTRUCTURE
        )
        if defaultServletName is not None:
            defaultServletHandlerDef.getPropertyValues().add(
                "defaultServletName", defaultServletName
            )

        defaultServletHandlerName: str = (
            parserContext.getReaderContext().generateBeanName(
                defaultServletHandlerDef
            )
        )
        parserContext.getRegistry().registerBeanDefinition(
            defaultServletHandlerName, defaultServletHandlerDef
        )
        parserContext.registerComponent(
            BeanComponentDefinition(
                defaultServletHandlerDef, defaultServletHandlerName
            )
        )

        urlMap = dict()
        urlMap["/**"] = defaultServletHandlerName

        handlerMappingDef = RootBeanDefinition()
        handlerMappingDef.setSource(source)
        handlerMappingDef.setRole(BeanDefinitionInterface.ROLE_INFRASTRUCTURE)
        handlerMappingDef.getPropertyValues().add("urlMap", urlMap)

        handlerMappingBeanName: str = (
            parserContext.getReaderContext().generateBeanName(
                handlerMappingDef
            )
        )
        parserContext.getRegistry().registerBeanDefinition(
            handlerMappingBeanName, handlerMappingDef
        )
        parserContext.registerComponent(
            BeanComponentDefinition(handlerMappingDef, handlerMappingBeanName)
        )

        # Ensure BeanNameUrlHandlerMapping (SPR-8289) and default HandlerAdapters are not "turned off"
        registerDefaultComponents(parserContext, source)
