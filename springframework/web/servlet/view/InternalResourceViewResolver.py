from springframework.web.servlet.view.UrlBasedViewResolver import (
    UrlBasedViewResolver,
)
from springframework.web.servlet.view.AbstractUrlBasedView import (
    AbstractUrlBasedView,
)
from springframework.web.servlet.view.InternalResourceView import (
    InternalResourceView,
)
from springframework.web.servlet.view.JstlView import JstlView


class InternalResourceViewResolver(UrlBasedViewResolver):
    _jstlPresent = True
    alwaysInclude = None
    # ClassUtils.isPresent("javax.servlet.jsp.jstl.core.Config", InternalResourceViewResolver.class.getClassLoader())

    def __init__(self, prefix: str = None, suffix: str = None):
        super().__init__()
        viewClass = self.required_view_class()
        if InternalResourceView == viewClass and self._jstlPresent:
            viewClass = JstlView
        self.set_view_class(viewClass)

        if (prefix is not None) and (suffix is not None):
            self.set_prefix(prefix)
            self.set_suffix(suffix)

    def set_always_include(self, alwaysInclude: bool) -> None:
        self.alwaysInclude = alwaysInclude

    def required_view_class(self):
        return InternalResourceView

    def instantiate_view(self) -> AbstractUrlBasedView:
        if self.get_view_class() == InternalResourceView:
            return InternalResourceView()
        elif self.get_view_class() == JstlView:
            return JstlView()
        else:
            return super().instantiate_view()

    def build_view(self, viewName: str) -> AbstractUrlBasedView:
        view = super().build_view(viewName)
        if self.alwaysInclude is not None:
            view.set_always_include(self.alwaysInclude)

        view.set_prevent_dispatch_loop(True)
        return view
