from springframework.beans.factory.config import BeanDefinitionInterface
from springframework.beans.factory.xml import ParserContext
from abc import ABC, abstractmethod
from unittest import mock


class MvcNamespaceUtils(mock.MagicMock):

    BEAN_NAME_URL_HANDLER_MAPPING_BEAN_NAME = (
        "BeanNameUrlHandlerMapping.class.getName()"
    )
    SIMPLE_CONTROLLER_HANDLER_ADAPTER_BEAN_NAME = (
        "SimpleControllerHandlerAdapter.class.getName()"
    )
    HTTP_REQUEST_HANDLER_ADAPTER_BEAN_NAME = (
        "HttpRequestHandlerAdapter.class.getName()"
    )
    URL_PATH_HELPER_BEAN_NAME = "mvcUrlPathHelper"
    PATH_MATCHER_BEAN_NAME = "mvcPathMatcher"
    CORS_CONFIGURATION_BEAN_NAME = "mvcCorsConfigurations"
    HANDLER_MAPPING_INTROSPECTOR_BEAN_NAME = "mvcHandlerMappingIntrospector"

    def registerDefaultComponents(
        self, parserContext: ParserContext, source=None
    ):
        # TODO
        # registerBeanNameUrlHandlerMapping(parserContext, source)
        # registerHttpRequestHandlerAdapter(parserContext, source)
        # registerSimpleControllerHandlerAdapter(parserContext, source)
        # registerHandlerMappingIntrospector(parserContext, source)
        # registerThemeResolver(parserContext, source)
        # registerLocaleResolver(parserContext, source)
        # registerFlashMapManager(parserContext, source)
        # registerViewNameTranslator(parserContext, source)
        pass
