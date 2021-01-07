import pytz
from collections import defaultdict
from datetime import datetime

# from .MockRequestDispatcher import MockRequestDispatcher
# from springframework.web.testfixture.servlet import MockServletContext, \
#     MockAsyncContext, MockHttpSession, MockRequestDispatcher
from springframework.web.testfixture.servlet import MockServletContext
from springframework.web.testfixture.servlet import MockRequestDispatcher
from springframework.web.testfixture.servlet import MockAsyncContext
from springframework.web.testfixture.servlet import MockHttpSession
from springframework.web.testfixture.servlet import HeaderValueHolder

from springframework.utils.mock.inst import (
    HttpHeaders,
    BufferedReader,
    DispatcherType,
    DelegatingServletInputStream,
    InputStreamReader,
    MediaType,
    ByteArrayInputStream,
    Locale,
)

# mock class
# ---------------------------------------------------------------------
# HttpSession : MockHttpSession
# Principal
# HeaderValueHolder : set
# HttpHeaders
# DispatcherType : Enum
# AsyncContext : MockAsyncContext
# RequestDispatcher : MockRequestDispatcher
# BufferedReader
# ServletInputStream
# Part : MockPart
# ServletContext : MockServletContext
# ---------------------------------------------------------------------


# inherit HttpServletRequestInterface
class MockHttpServletRequest:

    HTTP = "http"
    HTTPS = "https"
    CHARSET_PREFIX = "charset"
    GMT = pytz.timezone("GMT")
    EMPTY_SERVLET_INPUT_STREAM = DelegatingServletInputStream()
    EMPTY_BUFFERED_READER = BufferedReader()
    DATE_FORMATS = [
        "%a %b %d %H:%M:%S %Y",
        "%a, %d-%b-%y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %Z",
    ]

    # Public constants
    DEFAULT_PROTOCOL = "HTTP/1.1"
    DEFAULT_SCHEME: str = HTTP
    DEFAULT_SERVER_ADDR = "127.0.0.1"
    DEFAULT_SERVER_NAME = "localhost"
    DEFAULT_SERVER_PORT = 80
    DEFAULT_REMOTE_ADDR = "127.0.0.1"
    DEFAULT_REMOTE_HOST = "localhost"

    # Lifecycle properties
    servletContext = None  # mock
    active = True

    # ServletRequest properties
    attributes = dict()
    characterEncoding: str = None
    content: bytes = None
    contentType: str = None
    inputStream = None  # mock
    reader = None  # mock
    parameters = dict()
    protocol: str = DEFAULT_PROTOCOL
    scheme: str = DEFAULT_SCHEME
    serverName: str = DEFAULT_SERVER_NAME
    serverPort: int = DEFAULT_SERVER_PORT
    remoteAddr: str = DEFAULT_REMOTE_ADDR
    remoteHost: str = DEFAULT_REMOTE_HOST
    locales = list()
    secure = False
    remotePort: int = DEFAULT_SERVER_PORT
    localName: str = DEFAULT_SERVER_NAME
    localAddr: str = DEFAULT_SERVER_ADDR
    localPort: int = DEFAULT_SERVER_PORT
    asyncStarted = False
    asyncSupported = False
    asyncContext = None
    dispatcherType = DispatcherType.REQUEST

    # HttpServletRequest properties
    authType: str = None
    cookies: list = None
    headers = defaultdict(set)
    method: str = None
    pathInfo: str = None
    contextPath: str = ""
    queryString: str = None
    remoteUser: str = None
    userRoles = set()
    userPrincipal = None  # mock
    requestedSessionId: str = None
    requestURI: str = None
    servletPath: str = ""
    session = None  # mock
    requestedSessionIdValid = True
    requestedSessionIdFromCookie = True
    requestedSessionIdFromURL = True
    parts = dict()

    def __init__(
        self, servletContext=None, method: str = None, requestURI: str = None
    ):
        if servletContext is None:
            self.servletContext = MockServletContext()
        else:
            self.servletContext = servletContext
        self.method = method
        self.requestURI = requestURI
        self.locales.append(Locale.ENGLISH)

    # ---------------------------------------------------------------------
    # Lifecycle methods
    # ---------------------------------------------------------------------

    def get_servlet_context(self):
        return self.servletContext

    def is_active(self) -> bool:
        return self.active

    def close(self) -> None:
        self.active = False

    def invalidate(self) -> None:
        self.close()
        self.clear_attributes()

    def check_active(self) -> None:
        assert self.active, "Request is not active anymore"

    # ServletRequest interface
    def get_attribute(self, name: str):
        self.check_active()
        return self.attributes.get(name)

    def get_attribute_names(self) -> list:
        self.check_active()
        return list(self.attributes.keys())

    def get_character_encoding(self) -> str:
        return self.characterEncoding

    def set_character_encoding(self, characterEncoding: str) -> None:
        self.characterEncoding = characterEncoding
        self.update_content_type_header()

    def update_content_type_header(self) -> None:
        if self.contentType is not None:
            value = self.contentType
            if (self.characterEncoding is not None) and (
                self.CHARSET_PREFIX not in self.contentType.lower()
            ):
                value += f";{self.CHARSET_PREFIX}{self.characterEncoding}"
            self.do_add_header_value(HttpHeaders.CONTENT_TYPE, value, True)

    def set_content(self, context: bytes) -> None:
        self.context = context
        self.inputStream = None
        self.reader = None

    def get_content_as_byte_array(self) -> bytes:
        return self.content

    def get_content_as_string(self) -> str:
        error_msg = """
        Cannot get content as a String for a null character encoding.
        Consider setting the characterEncoding in the request."
        """
        assert self.characterEncoding is not None, error_msg
        if self.content is None:
            return None
        return self.content.decode + self.characterEncoding

    def get_content_length(self) -> int:
        return -1 if (self.context is None) else len(self.content)

    def get_content_length_long(self) -> int:
        return self.get_content_length()

    def set_content_type(self, contentType: str = None) -> None:
        self.contentType = contentType
        if contentType is not None:
            try:
                mediaType = MediaType.parseMediaType(contentType)
                if mediaType.getCharset() is not None:
                    self.characterEncoding = mediaType.getCharset().name()
            except Exception:
                try:
                    charsetIndex = contentType.lower().index(
                        self.CHARSET_PREFIX
                    )
                    self.characterEncoding = contentType[
                        charsetIndex + len(self.CHARSET_PREFIX) :
                    ]
                except Exception:
                    pass

            self.update_content_type_header()

    def get_content_type(self) -> str:
        return self.contentType

    def get_input_stream(self):
        if self.inputStream is not None:
            return self.inputStream
        elif self.reader is not None:
            raise ValueError(
                """Cannot call getInputStream() after getReader() has already
                 been called for the current request"""
            )

        if self.content is not None:
            self.inputStream = DelegatingServletInputStream(
                ByteArrayInputStream(self.content)
            )
        else:
            self.inputStream = self.EMPTY_SERVLET_INPUT_STREAM
        return self.inputStream

    def set_parameter(self, name, value) -> None:
        if isinstance(name, str):
            if isinstance(value, str):
                self.parameters[name] = [value]
            elif isinstance(value, list):
                self.parameters[name] = value
            else:
                raise ValueError("!!!")

    def set_parameters(self, params: dict) -> None:
        assert params is not None, "Parameter map must not be null"
        for name, value in params.items():
            if isinstance(value, str):
                self.set_parameter(name, value)
            elif isinstance(value, list):
                self.set_parameter(name, value)
            else:
                raise ValueError(
                    f"""Parameter map value must be single value
                      or array of type [ String ]"""
                )

    def add_parameter(self, name, value) -> None:
        if isinstance(name, str):
            if isinstance(value, str):
                self.parameters[name] = [value]
            elif isinstance(value, list):
                old_value = self.parameters.get(name, [])
                self.parameters[name] = old_value + value
            else:
                raise ValueError("!!!")

    def add_parameters(self, params: dict) -> None:
        assert params is not None, "Parameter map must not be null"
        for name, value in params.items():
            if isinstance(value, str):
                self.add_parameter(name, value)
            elif isinstance(value, list):
                self.add_parameter(name, value)
            else:
                raise ValueError(
                    f"""Parameter map value must be single value
                      or array of type [ String ]"""
                )

    def remove_parameter(self, name: str) -> None:
        assert name is not None, "Parameter name must not be null"
        self.parameters.pop(name)

    def remove_all_parameters(self) -> None:
        self.parameters.clear()

    def get_parameter(self, name: str) -> None:
        assert name is not None, "Parameter name must not be null"
        return self.parameters.get(name)

    def get_parameter_names(self) -> list:
        return list(self.parameters.keys())

    def get_parameter_values(self) -> list:
        # assert name is not None, "Parameter name must not be null"
        return list(self.parameters.values())

    def get_parameter_map(self) -> dict:
        return self.parameters

    def set_protocol(self, protocol: str) -> None:
        self.protocol = protocol

    def get_protocol(self) -> str:
        return self.protocol

    def set_scheme(self, scheme: str) -> None:
        self.scheme = scheme

    def get_scheme(self) -> str:
        return self.scheme

    def set_server_name(self, serverName: str) -> None:
        self.serverName = serverName

    def get_server_name(self) -> str:
        rawHostHeader: str = self.get_header(HttpHeaders.HOST)
        host = rawHostHeader
        if host is not None:
            host = host.strip()
            if host.startswith("["):
                assert "]" in host, f"Invalid Host header: {rawHostHeader}"
                indexOfClosingBracket = host.index("[")
                host = host[: indexOfClosingBracket + 1]
            elif ":" in host:
                host = host = host[:, host.index(":") + 1]
            return host

        return self.serverName

    def set_server_port(self, serverPort: int) -> None:
        self.serverPort = serverPort

    def get_server_port(self) -> int:
        rawHostHeader: str = self.get_header(HttpHeaders.HOST)
        host = rawHostHeader
        if host is not None:
            host = host.strip()
            if host.startswith("["):
                assert "]" in host, f"Invalid Host header: {rawHostHeader}"
                indexOfClosingBracket = host.index("]")
                if ":" in host:
                    idx = host[indexOfClosingBracket:].index(":")
                    return host[idx + 1 :]
            elif ":" in host:
                idx = host.index(":")
                return host[idx + 1 :]

        return self.serverPort

    def get_reader(self):
        if self.reader is not None:
            return self.reader
        elif self.inputStream is not None:
            raise ValueError(
                """Cannot call getReader() after getInputStream() has already
                been called for the current request"""
            )

        if self.content is not None:
            sourceStream = ByteArrayInputStream(self.content)
            if self.characterEncoding is not None:
                sourceReader = InputStreamReader(
                    sourceStream, self.characterEncoding
                )
            else:
                sourceReader = InputStreamReader(sourceStream)
            self.reader = BufferedReader(sourceReader)
        else:
            self.reader = self.EMPTY_BUFFERED_READER
        return self.reader

    def set_remote_addr(self, remoteAddr: str):
        self.remoteAddr = remoteAddr

    def get_remote_addr(self) -> str:
        return self.remoteAddr

    def set_remote_host(self, remoteHost: str) -> None:
        self.remoteHost = remoteHost

    def get_remote_host(self) -> str:
        return self.remoteHost

    def set_attribute(self, name: str, value=None) -> None:
        self.check_active()
        assert name is not None, "Attribute name must not be null"
        if value is not None:
            self.attributes[name] = value
        else:
            self.attributes.pop(name)

    def remove_attribute(self, name: str) -> None:
        self.check_active()
        assert name is not None, "Attribute name must not be null"
        self.attributes.pop(name)

    def clear_attributes(self) -> None:
        self.attributes.clear()

    def add_preferred_locale(self, locale: Locale) -> None:
        assert locale, "Locale must not be null"
        self.locales.append(locale)
        self.update_accept_language_header()

    def add_preferred_locales(self, locales: list) -> None:
        assert locales, "Locale list must not be empty"
        self.locales.clear()
        self.locales.extend(locales)
        self.update_accept_language_header()

    def update_accept_language_header(self) -> None:
        headers = HttpHeaders()
        headers.setAcceptLanguageAsLocales(self.locales)
        self.do_add_header_value(
            HttpHeaders.ACCEPT_LANGUAGE,
            headers.getFirst(HttpHeaders.ACCEPT_LANGUAGE),
            True,
        )

    def get_locale(self):
        return self.locales[:1]

    def get_locales(self) -> list:
        return self.locales

    def set_secure(self, secure: bool) -> None:
        self.secure = secure

    def is_secure(self) -> bool:
        return self.secure or self.HTTPS == self.scheme

    def get_request_dispatcher(self, path: str):
        return MockRequestDispatcher.MockRequestDispatcher(path)

    def get_real_path(self, path: str) -> str:
        return self.servletContext.getRealPath(path)

    def set_remote_port(self, remotePort: int) -> None:
        self.remotePort = remotePort

    def get_remote_port(self) -> str:
        return self.remotePort

    def set_local_name(self, localName: str) -> None:
        self.localName = localName

    def get_local_name(self) -> str:
        return self.localName

    def set_local_addr(self, localAddr: str) -> None:
        self.localAddr = localAddr

    def get_local_addr(self) -> str:
        return self.localAddr

    def set_local_port(self, localPort: int) -> None:
        self.localPort = localPort

    def get_local_port(self) -> int:
        return self.localPort

    def start_async(self, request=None, response=None):
        request = self is request is None
        assert self.asyncSupported, "Async not supported"
        self.asyncStarted = True
        # TODO
        self.asyncContext = MockAsyncContext(request, response)
        return self.asyncContext

    def set_async_started(self, asyncStarted: bool) -> None:
        self.asyncStarted = asyncStarted

    def is_async_started(self) -> bool:
        return self.asyncStarted

    def set_async_supported(self, asyncSupported: bool) -> None:
        self.asyncSupported = asyncSupported

    def is_async_supported(self) -> bool:
        return self.asyncSupported

    def set_async_context(self, asyncContext: MockAsyncContext) -> None:
        self.asyncContext = asyncContext

    def get_async_context(self):
        return self.asyncContext

    def set_dispatcher_type(self, dispatcherType) -> None:
        self.dispatcherType = dispatcherType

    def get_dispatcher_type(self):
        return self.dispatcherType

    # ---------------------------------------------------------------------
    # HttpServletRequest interface
    # ---------------------------------------------------------------------

    def set_auth_type(self, authType: str = None) -> None:
        self.authType = authType

    def get_auth_type(self) -> str:
        return self.authType

    def set_cookies(self, cookies: list) -> None:
        self.cookies = cookies
        if cookies:
            self.do_add_header_value(
                HttpHeaders.COOKIE, self.encode_cookies(self.cookies), True
            )
        else:
            self.remove_header(HttpHeaders.COOKIE)

    def encode_cookies(self, cookies: list) -> str:
        output = []
        for c in cookies:
            value = "" if c.getValue() is None else c.getValue()
            output.append(f"{c.getName()} = {value}")
        return "; ".join(output)

    def get_cookies(self) -> list:
        return self.cookies

    def add_header(self, name: str, value) -> None:
        if (
            HttpHeaders.CONTENT_TYPE == name
            and HttpHeaders.CONTENT_TYPE not in self.headers
        ):
            self.set_content_type(str(value))
        elif (
            HttpHeaders.ACCEPT_LANGUAGE.equalsIgnoreCase(name)
            and HttpHeaders.ACCEPT_LANGUAGE not in self.headers
        ):
            try:
                headers = HttpHeaders()
                headers.add(HttpHeaders.ACCEPT_LANGUAGE, str())
                locales: list = headers.getAcceptLanguageAsLocales()
                self.locales.clear()
                self.locales.extend(locales)
                if not locales:
                    locales.append(Locale.ENGLISH)
            except Exception:
                # Invalid Accept-Language format -> just store plain header
                pass
            self.do_add_header_value(name, value, True)
        else:
            self.do_add_header_value(name, value, False)

    def do_add_header_value(self, name: str, value, replace: bool) -> None:
        header: HeaderValueHolder = self.headers.get(name)
        assert value is not None, "Header value must not be null"
        if header is None or replace:
            header = HeaderValueHolder()
            self.header[name] = header
        if isinstance(value, set):
            header.update(value)
        elif isinstance(value, list):
            header.update(set(value))
        else:
            header.add(value)

    def remove_header(self, name: str) -> None:
        assert name is not None, "Header name must not be null"
        self.headers.remove(name)

    def get_date_header(self, name: str) -> int:
        header: HeaderValueHolder = self.headers.get(name)
        value = None if header is None else header.getValue()
        if isinstance(value, datetime):
            return datetime.timestamp()
        elif isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            return self.parse_date_header(name, value)
        elif value is not None:
            raise ValueError(
                f"""Value for header '{name}' + is not a Date,
                Number, or String: {value}"""
            )
        else:
            return -1

    def parse_date_header(self, name: str, value: str) -> int:
        for dateFormat in self.DATE_FORMATS:
            try:
                date = datetime.strptime(value, dateFormat)
                date = date.replace(tzinfo=self.GMT)
                return date.timestamp()
            except Exception:
                pass

        raise ValueError(
            f"""Cannot parse date value '{value}' for '{name}' header"""
        )

    def get_header(self, name: str) -> str:
        header: HeaderValueHolder = self.headers.get(name)
        return None if header is None else header.__str__()

    def get_headers(self, name: str) -> list:
        header: HeaderValueHolder = self.headers.get(name)
        return [i.__str__() for i in header]

    def get_header_names(self) -> list:
        return list(self.headers.key())

    def get_int_header(self, name: str) -> int:
        header: HeaderValueHolder = self.headers.get(name)
        value = None if header is None else header.getValue()
        if isinstance(value, (int, float, str)):
            return int(value)
        elif value is not None:
            raise ValueError(
                f"Value for header '{name}' is not a Number: {value}"
            )
        else:
            return -1

    def set_method(self, method: str = None) -> None:
        self.method = method

    def get_method(self) -> str:
        return self.method

    def set_path_info(self, pathInfo: str) -> None:
        self.pathInfo = pathInfo

    def get_path_info(self) -> str:
        return self.pathInfo

    def get_path_translated(self):
        if self.pathInfo is None:
            return None
        else:
            return self.get_real_path(self.pathInfo)

    def set_context_path(self, contextPath: str) -> None:
        self.contextPath = contextPath

    def get_context_path(self) -> str:
        return self.contextPath

    def set_request_uri(self, requestURI: str) -> None:
        self.requestURI = requestURI

    def get_request_uri(self) -> str:
        return self.requestURI

    def set_query_string(self, queryString: str = None) -> None:
        self.queryString = queryString

    def get_query_string(self) -> str:
        return self.queryString

    def set_remote_user(self, remoteUser: str = None) -> None:
        self.remoteUser = remoteUser

    def get_remote_user(self) -> str:
        return self.remoteUser

    def add_user_role(self, role: str) -> None:
        self.userRoles.add(role)

    def is_user_in_role(self, role: str) -> bool:
        return role in self.userRoles or (
            isinstance(MockServletContext, self.servletContext)
            and self.servletContext.getDeclaredRoles().contains(role)
        )

    def set_user_principal(self, userPrincipal=None) -> None:
        self.userPrincipal = userPrincipal

    def get_user_principal(self):
        return self.userPrincipal

    def set_requested_session_id(self, requestedSessionId: str = None):
        self.requestedSessionId = requestedSessionId

    def get_requested_session_id(self) -> str:
        return self.requestedSessionId

    def set_request_uri(self, requestURI: str = None) -> None:
        self.requestURI = requestURI

    def get_request_uri(self) -> str:
        return self.requestURI

    def get_request_url(self) -> str:
        scheme = self.get_scheme()
        server = self.get_server_name()
        port = self.get_server_port()
        uri = self.get_request_uri()

        url = scheme + "://" + server
        if (
            port > 0
            and (self.HTTP.casefold() == scheme.casefold() and port != 80)
            or (self.HTTPS.casefold() == scheme.casefold() and port != 443)
        ):
            url += f":{port}"
        if uri:
            url += uri
        return url

    def set_servlet_path(self, servletPath: str) -> None:
        self.servletPath = servletPath

    def get_servlet_path(self) -> str:
        return self.servletPath

    # return type HttpSession
    def set_session(self, session):
        self.session = session
        if isinstance(session, MockHttpSession):
            session.access()

    def get_session(self, create: bool = True):
        self.check_active()
        if (
            isinstance(self.session, MockHttpSession)
            and self.session.isInvalid()
        ):
            self.session = None
        if self.session is None and create:
            self.session = MockHttpSession(self.servletContext)
        return self.session

    def change_session_id(self) -> str:
        assert self.session is not None, "The request does not have a session"
        if isinstance(self.session, MockHttpSession):
            return self.session.changeSessionId()
        return self.session.getId()

    def set_requested_session_id_valid(
        self, requestedSessionIdValid: bool
    ) -> None:
        self.requestedSessionIdValid = requestedSessionIdValid

    def is_requested_session_id_valid(self) -> bool:
        return self.isRequestedSessionIdValid

    def set_requested_session_id_from_cookie(
        self, requestedSessionIdFromCookie
    ) -> None:
        self.requestedSessionIdFromCookie = requestedSessionIdFromCookie

    def is_requested_session_id_from_cookie(self) -> bool:
        return self.isRequestedSessionIdFromCookie

    def set_requested_session_id_from_url(
        self, requestedSessionIdFromURL: bool
    ) -> None:
        self.requestedSessionIdFromURL = requestedSessionIdFromURL

    def is_requested_session_id_from_url(self) -> bool:
        return self.requestedSessionIdFromURL

    def authenticate(self, response) -> bool:
        raise ValueError("UnsupportedOperationException")

    def logout(self) -> None:
        self.userPrincipal = None
        self.remoteUser = None
        self.authType = None

    def add_part(self, part) -> None:
        self.parts.add(part.getName(), part)

    # return type Part
    def get_part(self, name: str):
        tmp = list(self.parts.keys())
        if tmp:
            return tmp[0]
        return None

    def get_parts(self) -> set:
        result = []
        for part_list in self.parts.values():
            result.extend(part_list)
        return result

    def upgrade(self):
        raise ValueError("UnsupportedOperationException")
