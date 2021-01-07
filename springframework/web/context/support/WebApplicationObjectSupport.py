from abc import ABC

from springframework.context.ApplicationContext import ApplicationContext
from springframework.web.util.WebUtils import WebUtils
from springframework.web.context.support.WebApplicationContext import (
    WebApplicationContext,
)
from springframework.web.context.ServletContextAware import ServletContextAware
from springframework.context.support.ApplicationObjectSupport import (
    ApplicationObjectSupport,
)
from springframework.web.testfixture.servlet.MockServletContext import (
    MockServletContext as ServletContext,
)


class WebApplicationObjectSupport(
    ApplicationObjectSupport, ServletContextAware, ABC
):
    def __init__(self):
        self._servlet_context = None
        super().__init__()

    def set_servlet_context(self, servlet_context: ServletContext) -> None:
        if servlet_context is not self._servlet_context:
            self._servlet_context = servlet_context
            self.init_servlet_context(servlet_context)

    def is_context_required(self) -> bool:
        return True

    def init_application_context(
        self, context: ApplicationContext = None
    ) -> None:
        super().init_application_context(context)
        if self._servlet_context is None and isinstance(
            context, WebApplicationContext
        ):
            self._servlet_context = context.get_servlet_context()
            if self._servlet_context is not None:
                self.init_servlet_context(self._servlet_context)

    def init_servlet_context(self, servlet_context: ServletContext):
        pass

    def get_web_application_context(self):
        ctx: ApplicationContext = self.get_application_context()
        if isinstance(ctx, WebApplicationContext):
            return self.get_application_context()
        else:
            if self.is_context_required():
                raise ValueError(
                    "WebApplicationObjectSupport instance ["
                    + str(self)
                    + "] does not run in a WebApplicationContext but in: "
                    + ctx
                )
            else:
                return None

    def get_servlet_context(self):
        if self._servlet_context is not None:
            return self._servlet_context
        servlet_context = None
        wac: WebApplicationContext = self.get_web_application_context()
        if wac is not None:
            servlet_context = self.get_web_application_context()
        if servlet_context is None and self.is_context_required():
            raise ValueError(
                "WebApplicationObjectSupport instance ["
                + str(self)
                + "] does not run within a ServletContext. Make sure the object is fully configured!"
            )
        return servlet_context

    def get_temp_dir(self):
        servlet_context: ServletContext = self.get_servlet_context()
        if self._servlet_context is None:
            raise AssertionError("ServletContext is required")
        return WebUtils.get_temp_dir(servlet_context)
