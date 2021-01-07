import re
from datetime import datetime
from springframework.utils.mock.inst import ResourceBundle


class Cookie:

    TSPECIALS: str = '/()<>@,;:\\"[]?={} \t'
    LSTRING_FILE: str = "javax.servlet.http.LocalStrings"
    lStrings = ResourceBundle.getBundle(LSTRING_FILE)
    name = ""
    value = ""
    comment = ""
    domain = ""
    maxAge = -1
    path = ""
    secure = False
    version = 0
    isHttpOnly = False

    def __init__(self, name: str, value: str):
        if name is None or not name:
            raise ValueError("cookie_name_blank")
        if (
            name.casefold()
            in [
                "Comment",
                "Discard",
                "Domain",
                "Expires",
                "Max-Age",
                "Path",
                "Secure",
                "Version",
            ]
            or name.startswith("$")
            or self.is_token(name)
        ):
            raise ValueError("cookie_name_is_token")
        self.name = name
        self.value = value

    def set_comment(self, purpose: str) -> None:
        self.comment = purpose

    def get_comment(self) -> str:
        return self.comment

    def set_domain(self, domain: str) -> None:
        self.domain = domain.lower()

    def get_domain(self) -> str:
        return self.domain

    def set_max_age(self, expiry: int):
        self.maxAge = expiry

    def get_max_age(self) -> int:
        return self.maxAge

    def set_path(self, uri: str) -> None:
        self.path = uri

    def get_path(self) -> str:
        return self.path

    def set_secure(self, flag: bool) -> None:
        self.secure = flag

    def get_secure(self) -> bool:
        return self.secure

    def get_name(self) -> str:
        return self.name

    def set_value(self, newValue: str) -> None:
        self.value = newValue

    def get_value(self) -> str:
        return self.value

    def get_version(self) -> int:
        return self.Version

    def set_version(self, v: int) -> None:
        self.version = v

    def is_token(self, value: str) -> bool:
        for c in value:
            if c < 0x20 or c >= 0x7F or c in self.TSPECIALS:
                return False
        return True

    def set_http_only(self, isHttpOnly: bool) -> None:
        self.isHttpOnly = isHttpOnly

    def is_http_only(self) -> bool:
        return self.isHttpOnly


class MockCookie(Cookie):

    serialVersionUID: int = 4312531139502726325
    expires: datetime = None
    sameSite: str = None

    def __init__(self, name: str, value: str):
        super.__init__(name, value)

    def setExpi_ees(self, expires: datetime = None) -> None:
        self.expires = expires

    def get_expires(self, expires: datetime = None) -> None:
        return self.expires

    def set_same_site(self, sameSite: str = None) -> None:
        self.sameSite = sameSite

    def get_same_site(self) -> str:
        return self.sameSite

    def parse(self, setCookieHeader: str):
        assert setCookieHeader, "Set-Cookie header must not be null"
        cookieParts = re.split("\\s*=\\s*", setCookieHeader, 2)
        assert (
            len(cookieParts) == 2
        ), f"Invalid Set-Cookie header '{setCookieHeader}'"
        name = cookieParts[0]
        valueAndAttributes = re.split("\\s*;\\s*", cookieParts[1], 2)
        value = valueAndAttributes[0]
        if len(valueAndAttributes) > 1:
            attributes = re.split("\\s*;\\s*", valueAndAttributes[1])
        else:
            attributes = ""

        cookie = MockCookie(name, value)
        for attribute in attributes:
            if attribute.casefold() == "Domain":
                cookie.set_domain(
                    self.extract_attribute_value(attribute, setCookieHeader)
                )
            elif attribute.casefold() == "Max-Age":
                cookie.set_max_age(
                    int(
                        self.extract_attribute_value(
                            attribute, setCookieHeader
                        )
                    )
                )
            elif attribute.casefold() == "Expires":
                try:
                    attributeValues = self.extract_attribute_value(
                        attribute, setCookieHeader
                    )
                    RFC_1123_DATE_TIME_FORMAT = "%a, %-d %b %Y %I:%M:%S %Z"
                    cookie.set_expires(
                        datetime.strptime(
                            attributeValues, RFC_1123_DATE_TIME_FORMAT
                        )
                    )
                except Exception:
                    pass
            elif attribute.casefold() == "Path":
                cookie.set_path(
                    self.extract_attribute_value(attribute, setCookieHeader)
                )
            elif attribute.casefold() == "Secure":
                cookie.set_secure(True)
            elif attribute.casefold() == "HttpOnly":
                cookie.set_http_only(True)
            elif attribute.casefold() == "SameSite":
                cookie.set_same_site(
                    self.extract_attribute_value(attribute, setCookieHeader)
                )

        return cookie

    def extract_attribute_value(self, attribute: str, header: str) -> str:
        nameAndValue = attribute.split("=")
        assert (
            len(nameAndValue) == 2
        ), f"""No value in attribute '{nameAndValue[0]}' for
             Set-Cookie header '{header}'"""
        return nameAndValue[1]
