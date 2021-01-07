from abc import ABC, abstractmethod

from springframework.context.ApplicationContext import ApplicationContext
from springframework.web.testfixture.servlet import (
    MockServletContext as ServletContext,
)


class WebApplicationContext(ApplicationContext, ABC):
    ROOT_WEB_APPLICATION_CONTEXT_ATTRIBUTE = "WebApplicationContext.ROOT"
    SCOPE_REQUEST = "request"
    SCOPE_SESSION = "session"
    SCOPE_APPLICATION = "application"
    SERVLET_CONTEXT_BEAN_NAME = "servletContext"
    CONTEXT_PARAMETERS_BEAN_NAME = "contextParameters"
    CONTEXT_ATTRIBUTES_BEAN_NAME = "contextAttributes"

    @abstractmethod
    def get_servlet_context(self) -> ServletContext:
        raise NotImplementedError
