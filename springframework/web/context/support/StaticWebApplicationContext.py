from springframework.context.support.StaticApplicationContext import (
    StaticApplicationContext,
)
from springframework.utils.mock.inst import (
    ServletContextAwareProcessor,
    ServletContextAware,
    ServletConfigAware,
    WebApplicationContextUtils,
    ServletContextResource,
)


class StaticWebApplicationContext(StaticApplicationContext):

    servletContext = None
    servletConfig = None
    namespace: str = None
    themeSource = None

    def __init__(self):
        super().__init__()
        self.set_display_name("Root WebApplicationContext")

    def set_servlet_context(self, servletContext):
        self.servletContext = servletContext

    def get_servlet_context(self):
        return self.servletContext

    def set_namespace(self, namespace: str):
        self.namespace = namespace
        if namespace is None:
            self.set_display_name(
                f"WebApplicationContext for namespace '{namespace}'"
            )

    def get_namespace(self):
        return self.namespace

    def set_config_location(self, configLocation: str):
        raise Exception(
            "StaticWebApplicationContext does not support config locations"
        )

    def set_config_locations(self, configLocations: list):
        raise Exception(
            "StaticWebApplicationContext does not support config locations"
        )

    def get_config_locations(self) -> list:
        return None

    def post_process_bean_factory(self, beanFactory):
        beanFactory.addBeanPostProcessor(
            ServletContextAwareProcessor(
                self.servletContext, self.servletConfig
            )
        )
        beanFactory.ignoreDependencyInterface(ServletContextAware)
        beanFactory.ignoreDependencyInterface(ServletConfigAware)

        WebApplicationContextUtils.registerWebApplicationScopes(
            beanFactory, self.servletContext
        )
        WebApplicationContextUtils.registerEnvironmentBeans(
            beanFactory, self.servletContext, self.servletConfig
        )

    def get_resource_by_path(self, path: str):
        assert self.servletContext is not None, "No ServletContext available"
        return ServletContextResource(self.servletContext, path)
