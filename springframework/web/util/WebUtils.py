from abc import ABC
import os
from springframework.utils.mock.inst import (
    ServletRequest,
    HttpSession,
    ServletContext,
    HttpServletRequest,
)
from springframework.utils.mock.type import ServletRequestWrapper


class WebUtils(ABC):
    INCLUDE_REQUEST_URI_ATTRIBUTE = "javax.servlet.include.request_uri"
    INCLUDE_CONTEXT_PATH_ATTRIBUTE = "javax.servlet.include.context_path"
    INCLUDE_SERVLET_PATH_ATTRIBUTE = "javax.servlet.include.servlet_path"
    INCLUDE_PATH_INFO_ATTRIBUTE = "javax.servlet.include.path_info"
    INCLUDE_QUERY_STRING_ATTRIBUTE = "javax.servlet.include.query_string"
    FORWARD_REQUEST_URI_ATTRIBUTE = "javax.servlet.forward.request_uri"
    FORWARD_CONTEXT_PATH_ATTRIBUTE = "javax.servlet.forward.context_path"
    FORWARD_SERVLET_PATH_ATTRIBUTE = "javax.servlet.forward.servlet_path"
    FORWARD_PATH_INFO_ATTRIBUTE = "javax.servlet.forward.path_info"
    FORWARD_QUERY_STRING_ATTRIBUTE = "javax.servlet.forward.query_string"
    ERROR_STATUS_CODE_ATTRIBUTE = "javax.servlet.error.status_code"
    ERROR_EXCEPTION_TYPE_ATTRIBUTE = "javax.servlet.error.exception_type"
    ERROR_MESSAGE_ATTRIBUTE = "javax.servlet.error.message"
    ERROR_EXCEPTION_ATTRIBUTE = "javax.servlet.error.exception"
    ERROR_REQUEST_URI_ATTRIBUTE = "javax.servlet.error.request_uri"
    ERROR_SERVLET_NAME_ATTRIBUTE = "javax.servlet.error.servlet_name"
    CONTENT_TYPE_CHARSET_PREFIX = ";charset="
    DEFAULT_CHARACTER_ENCODING = "ISO-8859-1"
    TEMP_DIR_CONTEXT_ATTRIBUTE = "javax.servlet.context.tempdir"
    HTML_ESCAPE_CONTEXT_PARAM = "defaultHtmlEscape"
    RESPONSE_ENCODED_HTML_ESCAPE_CONTEXT_PARAM = "responseEncodedHtmlEscape"
    WEB_APP_ROOT_KEY_PARAM = "webAppRootKey"
    DEFAULT_WEB_APP_ROOT_KEY = "webapp.root"
    SUBMIT_IMAGE_SUFFIXES = [".x", ".y"]
    SESSION_MUTEX_ATTRIBUTE = "WebUtils" + ".MUTEX"

    @classmethod
    def set_web_app_root_system_property(
        cls, servlet_context: ServletContext
    ) -> None:
        if servlet_context is None:
            raise AssertionError("ServletContext must not be null")
        root = servlet_context.get_real_path("/")
        if root is None:
            raise InterruptedError(
                "Cannot set web app root system property when WAR file is not expanded"
            )
        param = servlet_context.get_init_parameter(cls.WEB_APP_ROOT_KEY_PARAM)
        key = param if param is not None else WebUtils.DEFAULT_WEB_APP_ROOT_KEY
        old_value = os.getenv(key)
        if old_value is not None and os.path.normcase(
            old_value
        ) != os.path.normcase(root):
            raise InterruptedError(
                "Web app root system property already set to different value: '"
                + key
                + "' = ["
                + old_value
                + "] instead of ["
                + root
                + "] - "
                + "Choose unique values for the 'webAppRootKey' context-param in your web.xml files!"
            )
        os.putenv(key, root)

    @classmethod
    def remove_web_app_root_system_property(
        cls, servlet_context: ServletContext
    ) -> None:
        if servlet_context is None:
            raise AssertionError("ServletContext must not be null")
        param = servlet_context.get_init_parameter(cls.WEB_APP_ROOT_KEY_PARAM)
        key = param if param is not None else cls.DEFAULT_WEB_APP_ROOT_KEY
        os.unsetenv(key)

    @classmethod
    def get_default_html_escape(cls, servlet_context: ServletContext):
        if servlet_context is None:
            return None
        param: str = servlet_context.get_init_parameter(
            cls.HTML_ESCAPE_CONTEXT_PARAM
        )
        return bool(param) if len(param.replace(" ", "")) > 0 else None

    @classmethod
    def get_response_encoded_html_escape(cls, servlet_context: ServletContext):
        if servlet_context is None:
            return None
        param: str = servlet_context.get_init_parameter(
            cls.RESPONSE_ENCODED_HTML_ESCAPE_CONTEXT_PARAM
        )
        return bool(param) if len(param.replace(" ", "")) > 0 else None

    @classmethod
    def get_temp_dir(cls, servlet_context: ServletContext):
        if servlet_context is None:
            raise AssertionError("ServletContext must not be null")
        return servlet_context.get_attribute(cls.TEMP_DIR_CONTEXT_ATTRIBUTE)

    @classmethod
    def get_real_path(cls, servlet_context: ServletContext, path: str):
        if servlet_context is None:
            raise AssertionError("ServletContext must not be null")
        if not path.startswith("/"):
            path = "/" + path
        real_path = servlet_context.get_real_path(path)
        if real_path is None:
            raise FileNotFoundError(
                f"""ServletContext resource [{path}] cannot be
                 resolved to absolute file path -
                 web application archive not expanded?"""
            )
        return real_path

    @classmethod
    def get_session_id(cls, request: HttpServletRequest):
        if request is None:
            raise AssertionError("Request must not be null")
        session: HttpSession = request.get_session(False)
        return session.get_id() if session is not None else None

    @classmethod
    def get_session_attribute(cls, request: HttpServletRequest, name: str):
        if request is None:
            raise AssertionError("Request must not be null")
        session: HttpSession = request.get_session(False)
        return session.get_attribute(name) if session is not None else None

    @classmethod
    def get_required_session_attribute(
        cls, request: HttpServletRequest, name: str
    ):
        attr = cls.get_session_attribute(request, name)
        if attr is None:
            raise InterruptedError("No session attribute '" + name + "' found")
        return attr

    @classmethod
    def set_session_attribute(
        cls, request: HttpServletRequest, name: str, value
    ):
        if request is None:
            raise AssertionError("Request must not be null")
        if value is not None:
            request.get_session().set_attribute(name, value)
        else:
            session: HttpSession = request.get_session(False)
            if session is not None:
                session.remove_attribute(name)

    @classmethod
    def get_session_mutex(cls, session: HttpSession):
        if session is None:
            raise AssertionError("Session must not be null")
        mutex = session.get_attribute(cls.SESSION_MUTEX_ATTRIBUTE)
        if mutex is None:
            mutex = session
        return mutex

    @classmethod
    def get_native_request(cls, request: ServletRequest, request_type):
        if request_type is not None:
            if isinstance(request_type, request.__class__):
                return request
            elif isinstance(request, ServletRequestWrapper):
                return cls.get_native_request(
                    request.get_request(), request_type
                )
        return None

    # TODO: Line 480
