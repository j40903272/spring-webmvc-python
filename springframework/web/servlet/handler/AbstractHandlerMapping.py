from abc import ABC, abstractmethod
from springframework.web.context.support import WebApplicationObjectSupport
from springframework.web.servlet import (
    HandlerMappingInterface as HandlerMapping,
)
from springframework.core import Ordered
from springframework.beans.factory import BeanNameAware

from springframework.web.util import UrlPathHelper
from springframework.web.util.pattern import PathPatternParser
from springframework.util import PathMatcher
from springframework.util import AntPathMatcher
from springframework.web.cors import CorsConfiguration
from springframework.web.cors import CorsConfigurationSource
from springframework.web.cors import CorsProcessor
from springframework.web.cors import DefaultCorsProcessor
from springframework.web.cors import UrlBasedCorsConfigurationSource
from springframework.web.cors import CorsUtils
from springframework.web.servlet import (
    HandlerInterceptorInterface as HandlerInterceptor,
)
from springframework.web.context.request import WebRequestInterceptor
from springframework.web.util import ServletRequestPathUtils
from springframework.web.servlet.HandlerExecutionChain import (
    HandlerExecutionChain,
)
from springframework.web.servlet.handler import MappedInterceptor
from springframework.utils.mock.inst import (
    HttpServletRequest,
    HttpServletResponse,
)
from springframework.web import HttpRequestHandler


class AbstractHandlerMapping(
    WebApplicationObjectSupport, HandlerMapping, Ordered, BeanNameAware, ABC
):
    defaultHandler = None
    patternParser: PathPatternParser = None
    urlPathHelper: UrlPathHelper = UrlPathHelper()
    pathMatcher: PathMatcher = PathMatcher()
    interceptors = list()  # list of object
    adaptedInterceptors = list()  # list of HandlerInterceptor
    corsConfigurationSource: CorsConfigurationSource = None
    corsProcessor: CorsProcessor = DefaultCorsProcessor()
    order: int = Ordered.LOWEST_PRECEDENCE
    beanName: str = None

    def set_default_handler(self, defaultHandler: object) -> None:
        self.defaultHandler = defaultHandler

    def get_default_handler(self) -> object:
        return self.defaultHandler

    def set_pattern_parser(self, patternParser: PathPatternParser) -> None:
        self.patternParser = patternParser

    def get_pattern_parser(self) -> PathPatternParser:
        return self.patternParser

    def set_always_use_full_path(self, alwasyUseFullPath: bool) -> None:
        self.urlPathHelper.set_always_use_full_path(alwasyUseFullPath)
        if isinstance(
            self.corsConfigurationSource, UrlBasedCorsConfigurationSource
        ):
            self.corsConfigurationSource.set_always_use_full_path(
                alwasyUseFullPath
            )

    def set_url_decode(self, urlDecode: bool) -> None:
        self.urlPathHelper.set_url_decode(urlDecode)
        if isinstance(
            self.corsConfigurationSource, UrlBasedCorsConfigurationSource
        ):
            self.corsConfigurationSource.set_url_decode(urlDecode)

    def set_remove_semicolon_content(
        self, removeSemicolonContent: bool
    ) -> None:
        self.urlPathHelper.set_remove_semicolon_content(removeSemicolonContent)
        if isinstance(
            self.corsConfigurationSource, UrlBasedCorsConfigurationSource
        ):
            self.corsConfigurationSource.set_remove_semicolon_content(
                removeSemicolonContent
            )

    def set_url_path_helper(self, urlPathHelper: UrlPathHelper) -> None:
        assert urlPathHelper, "UrlPathHelper must not be null"
        self.urlPathHelper = urlPathHelper
        if isinstance(
            self.corsConfigurationSource, UrlBasedCorsConfigurationSource
        ):
            self.corsConfigurationSource.set_url_path_helper(urlPathHelper)

    def get_url_path_helper(self) -> UrlPathHelper:
        return self.urlPathHelper

    def set_path_matcher(self, pathMatcher: PathMatcher) -> None:
        assert pathMatcher, "pathMatcher must not be null"
        if isinstance(
            self.corsConfigurationSource, UrlBasedCorsConfigurationSource
        ):
            self.corsConfigurationSource.set_path_matcher(pathMatcher)

    def get_path_matcher(self) -> PathMatcher:
        return self.pathMatcher

    def set_interceptors(self, *interceptors) -> None:
        for interceptor in interceptors:
            self.interceptors.append(interceptor)

    def set_cors_configurations(self, corsConfigurations: dict) -> None:
        if len(corsConfigurations) == 0:
            self.corsConfigurationSource = None
            return
        source = None
        if not self.get_pattern_parser() is None:
            source = UrlBasedCorsConfigurationSource(self.get_pattern_parser())
            source.set_cors_configurations(corsConfigurations)
        else:
            source = UrlBasedCorsConfigurationSource()
            source.set_cors_configurations(corsConfigurations)
            source.set_path_matcher(self.pathMatcher)
            source.set_url_path_helper(self.urlPathHelper)

        self.set_cors_configuration_source(source)

    def set_cors_configuration_source(
        self, source: CorsConfigurationSource
    ) -> None:
        assert (
            CorsConfigurationSource
        ), "CorsConfigurationSource must not be null"
        self.corsConfigurationSource = source
        if isinstance(source, UrlBasedCorsConfigurationSource):
            self.source.set_allow_init_lookup_path(False)

    def set_cors_processor(self, corsProcessor: CorsProcessor) -> None:
        assert corsProcessor, "CorsProcessor must not be null"
        self.corsProcessor = corsProcessor

    def get_cors_processor(self) -> CorsProcessor:
        return self.corsProcessor

    def set_order(self, order: int) -> None:
        self.order = order

    def get_order(self) -> int:
        return self.order

    def set_bean_name(self, name: str) -> None:
        self.beanName = name

    def format_mapping_name(self) -> str:
        if self.beanName is not None:
            return "'" + self.beanName + "'"
        return "<unknown>"

    def init_application_context(self, context=None) -> None:
        self.extend_interceptors(self.interceptors)
        self.detected_mapped_interceptors(self.interceptors)
        self.init_interceptors()

    def extend_interceptors(self, interceptors: list) -> None:
        pass

    def detected_mapped_interceptors(self, mappedInterceptors: list) -> None:
        # lack of BeanFactoryUtils
        pass

    def init_interceptors(self) -> None:
        if len(self.interceptors) != 0:
            for i in range(len(self.interceptors)):
                interceptor = self.interceptors[i]
                if interceptor is None:
                    raise ValueError(
                        f"Entry number {i} in interceptors array is null"
                    )
                self.adaptedInterceptors.append(
                    self.adapted_interceptors(interceptor)
                )

    def adapted_interceptor(self, interceptor: object) -> HandlerInterceptor:
        if isinstance(interceptor, HandlerInterceptor):
            return HandlerInterceptor(interceptor)
        elif isinstance(interceptor, WebRequestInterceptor):
            return interceptor
        else:
            raise ValueError(
                f"Interceptor type not supported: {type(interceptor).__name__}"
            )

    def get_adapted_interceptors(self) -> list:
        pass

    def get_mapped_interceptors(self) -> list:
        pass

    def uses_path_patterns(self) -> bool:
        return not self.get_pattern_parser() is None

    def get_handler(
        self, request: HttpServletRequest
    ) -> HandlerExecutionChain:
        handler = self.get_handler_internal(request)
        if handler is None:
            handler = self.get_default_handler()
        if handler is None:
            return None

        if isinstance(handler, str):
            handlerName = handler
            handler = self.obtain_application_context().get_bean(handlerName)

        executionChain = self.get_handler_execution_chain(handler, request)

        if self.has_cors_configuration_source(
            request
        ) or CorsUtils.is_pre_flight_request(request):
            config = self.get_cors_configuration(handler, request)
            if self.get_cors_configuration() is not None:
                globalConfig = self.get_cors_configuration_source().get_cors_configuration(
                    request
                )
                if globalConfig is not None:
                    config = globalConfig.combine(config)

            if config is not None:
                config.validate_allow_credentials()

            executionChain = self.get_cors_handler_execution_chain(
                request, executionChain, config
            )

        return executionChain

    @abstractmethod
    def get_handler_internal(self, request: HttpServletRequest):
        raise NotImplementedError

    def init_lookup_path(self, request: HttpServletRequest) -> str:
        if self.uses_path_patterns():
            request.remove_attribute(UrlPathHelper.PATH_ATTRIBUTE)
            requestPath = ServletRequestPathUtils.get_parsed_request_path(
                request
            )
            lookupPath = requestPath.path_within_application().value()
            return UrlPathHelper.defaultInstance.remove_semicolon_content(
                lookupPath
            )
        else:
            return self.get_url_path_helper().resolve_and_cache_lookup_path(
                request
            )

    def get_handler_execution_chain(
        self, handler: object, request: HttpServletRequest
    ) -> HandlerExecutionChain:
        chain = (
            handler
            if isinstance(handler, HandlerExecutionChain)
            else HandlerExecutionChain(handler)
        )

        for interceptor in self.adaptedInterceptors:
            if isinstance(interceptor, MappedInterceptor):
                mappedInterceptor: MappedInterceptor = interceptor
                if mappedInterceptor.matches(request):
                    chain.add_interceptor(mappedInterceptor.get_interceptor())
            else:
                chain.add_interceptor(interceptor)

        return chain

    def has_cors_configuration_source(self, handler: object) -> bool:
        if isinstance(handler, HandlerExecutionChain):
            handler = handler.get_handler()

        return (
            isinstance(handler, CorsConfigurationSource)
            or self.corsConfigurationSource is not None
        )

    def get_cors_configuration(
        self, handler: object, request: HttpServletRequest
    ) -> CorsConfiguration:
        resolvedHandler = handler
        if isinstance(handler, HandlerExecutionChain):
            resolvedHandler = HandlerExecutionChain(handler).get_handler()
        if isinstance(handler, CorsConfigurationSource):
            return CorsConfiguration(resolvedHandler).get_cors_configuration(
                request
            )
        return None

    def get_cors_handler_execution_chain(
        self,
        request: HttpServletRequest,
        chain: HandlerExecutionChain,
        config: CorsConfiguration,
    ):
        if CorsUtils.is_pre_flight_request(request):
            interceptors: [] = chain.get_interceptors()
            return HandlerExecutionChain(
                PreFlightHandler(config), interceptors
            )
        else:
            chain.add_interceptor(0, CorsInterceptor(config))
            return chain

    class PreFlightHandler(HttpRequestHandler, CorsConfiguration):

        config: CorsConfiguration = None

        def __init__(self, config: CorsConfiguration):
            self.config = config

        def handle_request(
            self, request: HttpServletRequest, response: HttpServletResponse
        ):
            corsProcessor.process_request(self.config, request, response)

        def get_cors_configuration(
            self, request: HttpServletRequest
        ) -> CorsConfiguration:
            return self.config

    class CorsInterceptor(HandlerInterceptor, CorsConfigurationSource):

        config: CorsConfiguration = None

        def __init__(self, config: CorsConfiguration):
            self.config = config

        def pre_handle(
            self,
            request: HttpServletRequest,
            response: HttpServletResponse,
            handler: object,
        ) -> bool:
            # mock preHandle behavior
            return True

        def get_cors_configuration(self, request: HttpServletRequest):
            return self.config
