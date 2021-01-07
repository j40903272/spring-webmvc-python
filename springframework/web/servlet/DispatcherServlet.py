from springframework.beans.factory.xml.MockXmlParser import MockXmlParser
from springframework.web.servlet.ModelAndView import ModelAndView
from springframework.web.servlet.handler import SimpleUrlHandlerMapping
from springframework.web.servlet.mvc.Controller import Controller
from springframework.web.servlet.mvc.SimpleControllerHandlerAdapter import (
    SimpleControllerHandlerAdapter,
)
from springframework.web.servlet.view import InternalResourceViewResolver
from springframework.utils.mock.inst import Locale


class MockController(Controller):
    def __init__(self, name: str):
        self.name = name

    def get_name(self) -> str:
        return self.name

    def handle_request(self, request, response) -> ModelAndView:
        print("handle")
        mv = ModelAndView()
        return mv


class MockSimpleUrlHandlerMapping(SimpleUrlHandlerMapping):
    def __init__(self, urlMap: dict(), mockLookupPath: str):
        super().__init__(urlMap)
        self.mockLookupPath = mockLookupPath

    def init_lookup_path(self, request):
        return self.mockLookupPath


class DispatcherServletMeta(type):
    def __init__(cls, *args, **kwargs):
        cls.OUTPUT_FLASH_MAP_ATTRIBUTE = (
            cls.__class__.__name__ + ".OUTPUT_FLASH_MAP"
        )
        cls.FLASH_MAP_MANAGER_ATTRIBUTE = (
            cls.__class__.__name__ + ".FLASH_MAP_MANAGER"
        )


class DispatcherServlet(metaclass=DispatcherServletMeta):
    """docstring for DispatcherServlet"""

    contextClass = None
    config = None
    webApplicationContext = None
    handlerMappings = []
    handlerAdapters = []
    viewResolvers = []
    xml_path = ""

    def __init__(self, xml_path):
        super(DispatcherServlet, self).__init__()
        print("inits")
        # self.arg = arg
        self.xml_path = xml_path

    def init(self, config):
        self.config = config

        """
        PropertyValues   pvs = new
        ServletConfigPropertyValues(getServletConfig(), this.requiredProperties);
        if (!pvs.isEmpty()) {
        try {
        BeanWrapper bw = PropertyAccessorFactory.forBeanPropertyAccess(this);
        ResourceLoader resourceLoader = new ServletContextResourceLoader(getServletContext());
        bw.registerCustomEditor(Resource.

        class , new ResourceEditor(resourceLoader, getEnvironment()));
        initBeanWrapper(bw);
        bw.setPropertyValues(pvs, true);
        }
        catch (BeansException ex) {
        if (logger.isErrorEnabled()) {

        logger.error("Failed to set bean properties on servlet '" + getServletName() + "'", ex);
        """
        self.init_servlet_bean()

    def init_servlet_bean(self):
        """
        getServletContext().log("Initializing Spring " + getClass().getSimpleName() + " '" + getServletName() + "'");
        if (logger.isInfoEnabled()) {
        logger.info("Initializing Servlet '" + getServletName() + "'");
        }
        long
        startTime = System.currentTimeMillis();
        """

        self.webApplicationContext = self.init_web_application_context()

    def init_web_application_context(self):
        context = None
        self.on_refresh(context)
        return 1

    def on_refresh(self, context):
        self.init_strategies(context)

    def init_strategies(self, context):
        mockXmlParser = MockXmlParser(self.xml_path)

        urlMap = mockXmlParser.get_url_map()
        prefix = mockXmlParser.get_view_resolver_attr()["prefix"]
        suffix = mockXmlParser.get_view_resolver_attr()["suffix"]

        simpleUrlHandlerMapping = mockXmlParser.get_class_by_name(
            "SimpleUrlHandlerMapping"
        )
        simpleUrlHandlerMapping.set_url_map(urlMap)
        simpleUrlHandlerMapping.init_application_context()
        self.handlerMappings.append(simpleUrlHandlerMapping)

        simpleHandlerAdapter = mockXmlParser.get_class_by_name(
            "SimpleControllerHandlerAdapter"
        )  # SimpleControllerHandlerAdapter()
        self.handlerAdapters.append(simpleHandlerAdapter)

        internalResourceViewResolver = mockXmlParser.get_class_by_name(
            "InternalResourceViewResolver"
        )  # InternalResourceViewResolver()
        internalResourceViewResolver.set_prefix(prefix)
        internalResourceViewResolver.set_suffix(suffix)
        self.viewResolvers.append(internalResourceViewResolver)

    def set_context_class(self, contextClass):
        self.contextClass = contextClass

    def do_service(self, request, response):
        self.do_dispatch(request, response)

    def do_dispatch(self, request, response):

        mapped_handler = self.get_handler(request)
        handler_adapter = self.get_handler_adapter(
            mapped_handler.get_handler()
        )

        if not mapped_handler.apply_pre_handle(request, response):
            return

        model_and_view = handler_adapter.handle(
            request, response, mapped_handler.get_handler()
        )
        mapped_handler.apply_post_handle(request, response, model_and_view)
        locale = Locale()
        view = self.resolve_view_name(model_and_view.get_view_name(), locale)
        view.render(model_and_view.get_model_internal(), request, response)

    def get_handler(self, request):
        for handlerMapping in self.handlerMappings:
            handler_execution_chain = handlerMapping.get_handler(request)
            if handler_execution_chain is not None:
                return handler_execution_chain
        return None

    def get_handler_adapter(self, handler):
        for handlerAdapter in self.handlerAdapters:
            if handlerAdapter.supports(handler):
                return handlerAdapter
        return None

    def resolve_view_name(self, viewName, locale):
        for viewResolver in self.viewResolvers:
            view = viewResolver.resolve_view_name(viewName, locale)
            if view is not None:
                return view
        return None
