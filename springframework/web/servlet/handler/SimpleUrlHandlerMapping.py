import logging
from springframework.web.servlet.handler import AbstractUrlHandlerMapping


class SimpleUrlHandlerMapping(AbstractUrlHandlerMapping):
    def __init__(self, urlMap: dict = None, order: int = None):
        super().__init__()
        self.urlMap = dict()
        self.lookup_path = ""
        if isinstance(urlMap, dict):
            self.set_url_map(urlMap)
        if isinstance(order, int):
            self.setOrder(order)

    def set_mappings(self, mappings: dict) -> None:
        self.urlMap.update(mappings)

    def set_url_map(self, urlMap: dict) -> None:
        self.urlMap.update(urlMap)

    def get_url_map(self) -> dict:
        return self.urlMap

    def init_application_context(self, context=None) -> None:
        super().init_application_context()
        self.register_handlers(self.urlMap)

    def register_handlers(self, urlMap: dict) -> None:
        if not urlMap:
            logging.info(f"No patterns in {self.format_mapping_name()}")
        else:
            for url, handler in urlMap.items():
                # Prepend with slash if not already present.
                if not url.startswith("/"):
                    url = "/" + url
                # Remove whitespace from handler bean name.
                if isinstance(handler, str):
                    handler = handler.strip()
                self.register_handler(url, handler)

            patterns = list()
            if self.get_root_handler() is not None:
                patterns.append("/")
            if self.get_default_handler() is not None:
                patterns.append("/**")
            patterns.extend(list(self.get_handler_map().keys()))
            logging.debug(
                f"Patterns {patterns} in {self.format_mapping_name()}"
            )
