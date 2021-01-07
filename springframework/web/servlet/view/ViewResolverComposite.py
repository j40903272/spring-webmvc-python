from springframework.utils.mock.inst import Ordered
from springframework.beans.factory.InitializingBean import InitializingBean
from springframework.context.ApplicationContextAware import (
    ApplicationContextAware,
)
from springframework.web.context.ServletContextAware import ServletContextAware
from .ViewResolver import ViewResolver
from .View import View


class ViewResolverComposite(
    ViewResolver,
    Ordered,
    InitializingBean,
    ApplicationContextAware,
    ServletContextAware,
):
    _viewResolvers = list()
    _order = Ordered.LOWEST_PRECEDENCE

    def setViewResolvers(self, viewResolvers: list) -> None:
        self._viewResolvers.clear()
        if not viewResolvers:
            self._viewResolvers.append(viewResolvers)

    def getViewResolvers(self) -> list:
        return self._viewResolvers

    def setOrder(self, order: int) -> None:
        self._order = order

    def getOrder(self) -> int:
        return self._order

    def setServletContext(self, servletContext: ServletContext) -> None:
        for viewResolver in self._viewResolvers:
            if isinstance(viewResolver, ServletContextAware):
                viewResolver.setServletContext(servletContext)

    def afterPropertiesSet(self) -> None:
        for viewResolver in self._viewResolvers:
            if isinstance(viewResolver, InitializingBean):
                viewResolver.afterPropertiesSet()

    def resolveViewName(viewName: str, locale: Locale) -> View:
        for viewResolver in self._viewResolvers:
            view = viewResolver.resolveViewName(viewName, locale)
            if view is not None:
                return view

        return None
