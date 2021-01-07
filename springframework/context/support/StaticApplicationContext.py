from unittest import mock
from springframework.beans.factory.config import (
    BeanDefinitionInterface as BeanDefinition,
)
from springframework.context.support.GenericApplicationContext import (
    GenericApplicationContext,
)
from springframework.utils.mock.inst import GenericBeanDefinition


class StaticApplicationContext(GenericApplicationContext):
    def __init__(self, parent=None):
        if parent:
            super().__init__(parent)
        else:
            super().__init__()
        self.staticMessageSource = mock.MagicMock(name="StaticMessageSource")
        # self.getBeanFactory().register_singleton(self.MESSAGE_SOURCE_BEAN_NAME, self.staticMessageSource)

    def assert_bean_factory_active(self):
        pass

    def get_static_message_source(self):
        return self.staticMessageSource

    def register_singleton(self, name: str, clazz, pvs=None):
        bd = GenericBeanDefinition()
        bd.set_bean_class(clazz)
        if pvs:
            bd.setPropertyValues(pvs)
        self.get_default_listable_bean_factory().register_bean_definition(
            name, bd
        )

    def register_prototype(self, name: str, clazz, pvs=None):
        bd = GenericBeanDefinition()
        bd.set_scope(BeanDefinition.SCOPE_PROTOTYPE)
        bd.set_bean_class(clazz)
        bd.set_property_values(pvs)
        self.get_default_listable_bean_factory().register_bean_definition(
            name, bd
        )

    def addMessage(self, code: str, locale, defaultMessage: str):
        self.get_static_message_source().addessage(
            code, locale, defaultMessage
        )
