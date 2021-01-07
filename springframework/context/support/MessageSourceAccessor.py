from springframework.context.MessageSource import MessageSource
from springframework.context.MessageSourceResolvable import (
    MessageSourceResolvable,
)
from typing import List

from springframework.utils.mock.inst import Locale, LocaleContextHolder


class MessageSourceAccessor:
    def __init__(
        self, message_source: MessageSource, default_locale: Locale = None
    ):
        self._message_source: MessageSource = message_source
        self._default_locale: Locale = default_locale

    def get_default_locale(self) -> Locale:
        return (
            self._default_locale
            if self._default_locale is not None
            else LocaleContextHolder.get_locale()
        )

    def get_message(
        self,
        code: str = None,
        default_message: str = None,
        locale: Locale = None,
        args: List[object] = None,
        resolvable: MessageSourceResolvable = None,
    ) -> str:
        if code is not None and default_message is not None:
            if locale is not None:
                if args is not None:
                    msg = self._message_source.get_message(
                        locale,
                        default_message=default_message,
                        code=code,
                        args=args,
                    )
                else:
                    msg = self._message_source.get_message(
                        locale, default_message=default_message, code=code
                    )
            else:
                if args is not None:
                    msg = self._message_source.get_message(
                        self.get_default_locale(),
                        default_message=default_message,
                        code=code,
                        args=args,
                    )
                else:
                    msg = self._message_source.get_message(
                        self.get_default_locale(),
                        default_message=default_message,
                        code=code,
                    )
            return msg if msg is not None else ""
        if code is not None:
            if args is not None:
                if locale is not None:
                    return self._message_source.get_message(
                        locale, code=code, args=args
                    )
                return self._message_source.get_message(
                    self.get_default_locale(), code=code, args=args
                )
            return self._message_source.get_message(
                self.get_default_locale(), code=code
            )
        if resolvable is not None:
            if locale is not None:
                return self._message_source.get_message(
                    locale, resolvable=resolvable
                )
            return self._message_source.get_message(
                self.get_default_locale(), resolvable=resolvable
            )
        raise ValueError("Invalid arguments")
