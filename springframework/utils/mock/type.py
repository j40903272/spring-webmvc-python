from unittest import mock

HttpSessionBindingListener = type(
    "HttpSessionBindingListener", (mock.MagicMock,), {}
)
Serializable = type("Serializable", (mock.MagicMock,), {})
HttpServletResponseWrapper = type(
    "HttpServletResponseWrapper", (mock.MagicMock,), {}
)
JstlView = type("JstlView", (mock.MagicMock,), {})
ServletRequestWrapper = type("ServletRequestWrapper", (mock.MagicMock,), {})
AsyncHandlerInterceptor = type(
    "AsyncHandlerInterceptor", (mock.MagicMock,), {}
)
Servlet = type("Servlet", (mock.MagicMock,), {})
HttpServletRequest = type("HttpServletRequest", (), {})
HttpServletResponse = type("HttpServletResponse", (), {})
HttpStatus = type("HttpStatus", (), {})
