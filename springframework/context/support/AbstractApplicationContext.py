from springframework.context.ConfigurableApplicationContext import (
    ConfigurableApplicationContext,
)
from springframework.core.io.DefaultResourceLoader import DefaultResourceLoader
from springframework.context.ApplicationContext import ApplicationContext


class AbstractApplicationContext(
    DefaultResourceLoader, ConfigurableApplicationContext
):
    def __init__(self):
        super().__init__()
        self.id: str = None
        self.parent: ApplicationContext = None
        self.startupDate = 0
        self.environment = None

    # ---------------------------------------------------------------------
    # Implementation of ApplicationContext interface
    # ---------------------------------------------------------------------

    def set_id(self, id: str) -> None:
        self.id = id

    def get_id(self) -> str:
        return self.id

    def get_application_name(self) -> str:
        return ""

    def set_display_name(self, displayName: str):
        assert displayName, "Display name must not be empty"
        self.displayName = displayName

    def get_display_name(self) -> str:
        return self.displayName

    def get_parent(self) -> ApplicationContext:
        return self.parent

    def set_environment(self, environment) -> None:
        self.environment = environment

    def get_environment(self):
        if self.environment is None:
            self.environment = self.create_environment()
        return self.environment

    def create_environment(self) -> None:
        return None

    def get_autowire_capable_bean_factory(self):
        return self.get_bean_factory()

    def get_startup_date(self):
        return self.startupDate

    # ---------------------------------------------------------------------
    #  Implementation of ConfigurableApplicationContext interface
    # ---------------------------------------------------------------------

    def refresh(self):
        pass

    # ---------------------------------------------------------------------
    #  Implementation of MessageSource interface
    # ---------------------------------------------------------------------

    # three other types
    def get_message(self, code: str, args: list, locale):
        return self.get_message_source().get_message(code, args, locale)
