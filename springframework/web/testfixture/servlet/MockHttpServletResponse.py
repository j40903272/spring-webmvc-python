import pytz
from wsgiref.handlers import format_date_time
from time import mktime
import time
from unittest import mock

from springframework.web.util.WebUtils import WebUtils
from springframework.web.testfixture.servlet.MockCookie import (
    Cookie,
    MockCookie,
)
from springframework.web.testfixture.servlet.HeaderValueHolder import (
    HeaderValueHolder,
)
from springframework.utils.mock.inst import (
    ByteArrayOutputStream,
    ResponseServletOutputStream,
    HttpHeaders,
    ServletOutputStream,
    MediaType,
    Locale,
)


class MockHttpServletResponse:
    def __init__(self):
        self.CHARSET_PREFIX = "charset="
        self.DATE_FORMAT = "%a %b %d %H:%M:%S %Y"
        self.GMT = pytz.timezone("GMT")

        # ServletResponse properties
        self.outputStreamAccessAllowed = True
        self.writerAccessAllowed = True
        self.characterEncoding = WebUtils.DEFAULT_CHARACTER_ENCODING
        self.charset = False
        self.content = ByteArrayOutputStream()
        self.outputStream = ResponseServletOutputStream()
        self.writer = None  # private PrintWriter writer
        self.contentLength = 0

        self.contentType: str = None
        self.bufferSize = 4096
        self.committed: bool = None
        self.locale = Locale.getDefault()

        # HttpServletResponse properties
        self.cookies = []
        self.headers = dict()
        self.status = 200  # HttpServletResponse.SC_OK
        self.errorMessage: str = None
        self.forwardedUrl: str = None
        self.includedUrls = []

    # ServletResponse interface
    def set_output_stream_access_allowed(
        self, outputStreamAccessAllowed: bool
    ) -> None:
        self.outputStreamAccessAllowed = outputStreamAccessAllowed

    def is_output_stream_access_allowed(self) -> bool:
        return self.outputStreamAccessAllowed

    def set_writer_access_allowed(self, writerAccessAllowed: bool) -> None:
        self.writerAccessAllowed = writerAccessAllowed

    def is_writer_access_allowed(self) -> bool:
        return self.writerAccessAllowed

    def is_charset(self) -> bool:
        return self.charset

    def set_character_encoding(self, characterEncoding: str) -> None:
        self.characterEncoding = characterEncoding
        self.charset = True
        self.update_content_type_property_and_header()

    def update_content_type_property_and_header(self) -> None:
        if self.contentType is not None:
            value = self.contentType
            if (
                self.charset
                and self.CHARSET_PREFIX not in self.contentType.lower()
            ):
                value = (
                    value + ";" + self.CHARSET_PREFIX + self.characterEncoding
                )
                self.contentType = value
            self.do_add_header_value(HttpHeaders.CONTENT_TYPE, value, True)

    def get_character_encoding(self) -> str:
        return self.characterEncoding

    def get_output_stream(self) -> ServletOutputStream:
        assert (
            self.outputStreamAccessAllowed
        ), "OutputStream access not allowed"
        return self.outputStream

    """
    @Override
    public PrintWriter getWriter() throws UnsupportedEncodingException {
        Assert.state(self.writerAccessAllowed, "Writer access not allowed");
        if (self.writer == null) {
            Writer targetWriter = (self.characterEncoding != null ?
                    new OutputStreamWriter(self.content,
                    self.characterEncoding) :
                    new OutputStreamWriter(self.content));
            self.writer = new ResponsePrintWriter(targetWriter);
        }
        return self.writer;
    }

    public byte[] getContentAsByteArray(self) -> :
        return self.content.toByteArray();
    }
    """

    def get_content_as_string(self) -> str:
        if self.characterEncoding is not None:
            return self.content.decode + self.characterEncoding
        else:
            self.content.toString()

    def get_content_as_string(self, fallbackCharset) -> str:  #: Charset
        if self.is_charset() and self.characterEncoding is not None:
            return self.content.decode + self.characterEncoding
        else:
            return fallbackCharset.name()

    def set_content_length(self, contentLength: int) -> None:
        self.contentLength = contentLength
        self.do_add_header_value(
            HttpHeaders.CONTENT_LENGTH, contentLength, True
        )

    def get_content_length(self) -> int:
        return int(self.contentLength)

    def set_content_length_long(self, contentLength: int) -> None:
        self.contentLength = contentLength
        self.do_add_header_value(
            HttpHeaders.CONTENT_LENGTH, contentLength, True
        )

    def get_content_length_long(self) -> int:
        return self.contentLength

    def set_content_type(self, contentType: str = None) -> None:
        self.contentType = contentType
        if contentType is not None:
            try:
                mediaType = MediaType.parseMediaType(contentType)
                if mediaType.getCharset() is not None:
                    self.characterEncoding = mediaType.getCharset().name()
                    self.charset = True
            except Exception:
                try:
                    charsetIndex = contentType.lower().index(
                        self.CHARSET_PREFIX
                    )
                    self.characterEncoding = contentType[
                        charsetIndex + len(self.CHARSET_PREFIX) :
                    ]
                    self.charset = True
                except Exception:
                    pass

            self.update_content_type_property_and_header()

    def get_content_type(self) -> str:
        return self.contentType

    def set_buffer_size(self, bufferSize: int) -> None:
        self.bufferSize = bufferSize

    def get_buffer_size(self) -> int:
        return self.bufferSize

    def flush_buffer(self) -> None:
        self.set_committed(True)

    def reset_buffer(self) -> None:
        assert (
            not self.is_committed()
        ), "Cannot reset buffer - response is already committed"
        self.content.reset()

    def set_committed_if_buffer_size_exceeded(self) -> None:
        bufSize = self.get_buffer_size()
        if bufSize > 0 and self.content.size() > bufSize:
            self.set_committed(True)

    def set_committed(self, committed: bool) -> None:
        self.committed = committed

    def is_committed(self) -> bool:
        return self.committed

    def reset(self) -> None:
        self.reset_buffer()
        self.characterEncoding = None
        self.charset = False
        self.contentLength = 0
        self.contentType = None
        self.locale = Locale.getDefault()
        self.cookies.clear()
        self.headers.clear()
        self.status = 200  # HttpServletResponse.SC_OK
        self.errorMessage = None

    def set_locale(self, locale: Locale) -> None:
        self.locale = locale
        self.do_add_header_value(
            HttpHeaders.CONTENT_LANGUAGE, locale.toLanguageTag(), True
        )

    def get_locale(self) -> Locale:
        return self.locale

    # HttpServletResponse interface
    def add_cookie(self, cookie: Cookie) -> None:
        assert cookie, "Cookie must not be null"
        self.cookies.append(cookie)
        self.do_add_header_value(
            HttpHeaders.SET_COOKIE, self.get_cookie_header(cookie), False
        )

    def get_cookie_header(self, cookie: Cookie) -> str:
        buf = ""
        buf += cookie.get_name() + "="
        if cookie.get_value() is None:
            buf += ""
        else:
            buf += cookie.get_value()
        if cookie.get_path():
            buf += "; Path=" + cookie.get_path()

        if cookie.get_domain():
            buf += "; Domain=" + cookie.get_domain()

        maxAge = cookie.get_max_age()
        if maxAge >= 0:
            buf += "; Max-Age=" + str(maxAge)
            buf += "; Expires="
            if isinstance(cookie, MockCookie):
                expires = cookie.get_expires()
            else:
                expires = None

            if expires is not None:
                stamp = mktime(expires.timetuple())
                buf += format_date_time(stamp)
            else:
                headers = HttpHeaders()
                if maxAge > 0:
                    headers.setExpires(
                        int(round(time.time() * 1000)) + 1000 * maxAge
                    )
                else:
                    headers.setExpires(0)
                buf += headers.getFirst(HttpHeaders.EXPIRES)

        if cookie.get_secure():
            buf += "; Secure"
        if cookie.is_http_only():
            buf += "; HttpOnly"
        if isinstance(cookie, MockCookie):
            if cookie.getSameSite():
                buf += "; SameSite=" + cookie.getSameSite()
        return buf

    # public Cookie[] getCookies(self):
    #   return self.cookies.toArray(new Cookie[0]);
    # }

    def get_cookie(self, name: str) -> Cookie:
        assert name, "Cookie name must not be null"
        for cookie in self.cookies:
            if name == cookie.getName():
                return cookie
        return None

    def contains_header(self, name: str) -> bool:
        return self.headers.get(name) is not None

    def get_header_names(self) -> set:
        return self.headers.keySet()

    def get_header(self, name: str) -> str:
        header = self.headers.get(name)
        if header is not None:
            return header.get_string_value()
        else:
            return None

    def get_headers(self, name: str) -> []:
        header = self.headers.get(name)
        if header is not None:
            return header.get_string_values()
        else:
            return []

    def get_header_value(self, name: str):
        header = self.headers.get(name)
        if header is not None:
            return header.get_value()
        else:
            return None

    def get_header_values(self, name: str) -> []:
        header = self.headers.get(name)
        if header is not None:
            return header.get_values()
        else:
            return []

    def encode_url(self, url: str) -> str:
        return url

    def encode_redirect_url(self, url: str) -> str:
        return self.encode_url(url)

    def send_error(self, status: int, errorMessage: str) -> None:
        assert (
            not self.is_committed()
        ), "Cannot set error status - response is already committed"
        self.status = status
        self.errorMessage = errorMessage
        self.set_committed(True)

    def send_error(self, status: int) -> None:
        assert (
            not self.is_committed()
        ), "Cannot set error status - response is already committed"
        self.status = status
        self.set_committed(True)

    def send_redirect(self, url: str) -> None:
        assert (
            not self.is_committed()
        ), "Cannot set error status - response is already committed"
        assert url, "Redirect URL must not be null"
        self.set_header(HttpHeaders.LOCATION, url)
        self.set_status(302)  # HttpServletResponse.SC_MOVED_TEMPORARILY
        self.set_committed(True)

    def get_redirected_url(self) -> str:
        return self.get_header(HttpHeaders.LOCATION)

    def set_date_header(self, name: str, value: int) -> None:
        self.set_header_value(name, self.format_date(value))

    def add_date_header(self, name: str, value: int) -> None:
        self.add_header_value(name, self.format_date(value))

    def get_date_header(self, name: str) -> int:
        headerValue = self.get_header(name)
        if headerValue is None:
            return -1
        try:
            return (
                self.new_date_format().parse(self.get_header(name)).getTime()
            )
        except Exception:
            raise ValueError(
                f"Value for header {name} is not a valid Date: {headerValue}"
            )

    # def format_date(self, date: int) -> str:
    #   return self.new_date_format().format(new Date(date))

    # private DateFormat new_date_format(self) -> :
    #   SimpleDateFormat dateFormat =
    # new SimpleDateFormat(DATE_FORMAT, Locale.US);
    #   dateFormat.setTimeZone(GMT);
    #   return dateFormat;
    # }

    def set_header(self, name: str, value: str) -> None:
        self.set_header_value(name, value)

    def add_header(self, name: str, value: str) -> None:
        self.add_header_value(name, value)

    def set_int_header(self, name: str, value: int) -> None:
        self.set_header_value(name, value)

    def add_int_header(self, name: str, value: int) -> None:
        self.add_header_value(name, value)

    def set_header_value(self, name: str, value) -> None:
        replaceHeader = True
        if self.set_special_header(name, value, replaceHeader):
            return
        self.do_add_header_value(name, value, replaceHeader)

    def add_header_value(self, name: str, value) -> None:
        replaceHeader = False
        if self.set_special_header(name, value, replaceHeader):
            return
        self.do_add_header_value(name, value, replaceHeader)

    def set_special_header(
        self, name: str, value, replaceHeader: bool
    ) -> bool:
        if isinstance(HttpHeaders, mock.MagicMock):
            return False
        elif HttpHeaders.CONTENT_TYPE.equalsIgnoreCase(name):
            self.set_content_type(str(value))
            return True
        elif HttpHeaders.CONTENT_LENGTH.equalsIgnoreCase(name):
            self.set_content_length(int(value))
            return True
        elif HttpHeaders.CONTENT_LANGUAGE.equalsIgnoreCase(name):
            contentLanguages = str(value)
            headers = HttpHeaders()
            headers.add(HttpHeaders.CONTENT_LANGUAGE, contentLanguages)
            language = headers.getContentLanguage()
            self.set_locale(language if language is not None else Locale)
            self.do_add_header_value(
                HttpHeaders.CONTENT_LANGUAGE, contentLanguages, True
            )
            return True
        elif HttpHeaders.SET_COOKIE.equalsIgnoreCase(name):
            cookie = MockCookie.parse(str(value))
            if replaceHeader:
                self.set_cookie(cookie)
            else:
                self.add_cookie(cookie)
            return True
        else:
            return False

    def do_add_header_value(
        self, name: str, value: object, replace: bool
    ) -> None:
        assert value, "Header value must not be null"

        if name not in self.headers:
            self.headers[name] = HeaderValueHolder()

        if replace:
            self.headers[name].set_value(value)
        else:
            self.headers[name].add_value(value)

    def set_cookie(self, cookie: Cookie) -> None:
        assert cookie, "Cookie must not be null"
        self.cookies.clear()
        self.cookies.append(cookie)
        self.do_add_header_value(
            HttpHeaders.SET_COOKIE, self.get_cookie_header(cookie), True
        )

    def set_status(self, status: int, errorMessage: str = None) -> None:
        if not self.is_committed():
            self.status = status
            self.errorMessage = errorMessage

    def get_status(self) -> int:
        return self.status

    def get_error_message(self) -> str:
        return self.errorMessage

    # Methods for MockRequestDispatcher
    def set_forwarded_url(self, forwardedUrl: str = None) -> None:
        self.forwardedUrl = forwardedUrl

    def get_forwarded_url(self) -> str:
        return self.forwardedUrl

    def set_included_url(self, includedUrl: str = None) -> None:
        self.includedUrls.clear()
        if includedUrl is not None:
            self.includedUrls.append(includedUrl)

    def get_included_url(self) -> str:
        count = len(self.includedUrls)
        assert (
            count <= 1
        ), f"""More than 1 URL included - check getIncludedUrls\
         instead: {self.includedUrls}"""
        return self.includedUrls[0] if count == 1 else None

    def add_included_url(self, includedUrl: str) -> None:
        assert includedUrl, "Included URL must not be null"
        self.includedUrls.append(includedUrl)

    def get_included_urls(self) -> []:
        return self.includedUrls
