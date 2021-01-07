from abc import ABC

from springframework.web.servlet.view.AbstractView import AbstractView
from springframework.beans.factory.InitializingBean import InitializingBean


class AbstractUrlBasedView(AbstractView, InitializingBean, ABC):
    url: str = None

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def set_url(self, url: str) -> None:
        self.url = url

    def get_url(self) -> str:
        return self.url

    def after_properties_set(self) -> None:
        if self.is_url_required() and self.get_url() is None:
            raise ValueError("Property 'url' is required")

    def is_url_required(self) -> bool:
        return True

    def check_resource(self, locale) -> bool:
        # local type: Locale
        return True

    def __str__(self) -> str:
        return super().__str__() + f"; URL [{self.get_url()}]"
