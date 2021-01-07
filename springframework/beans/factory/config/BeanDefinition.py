from springframework.beans import (
    BeanMetadataElement,
)  # , MutablePropertyValues
from springframework.core import AttributeAccessor  # , ResolvableType
from springframework.utils.mock.inst import ConfigurableBeanFactory


class BeanDefinitionInterface(AttributeAccessor, BeanMetadataElement):

    SCOPE_SINGLETON = ConfigurableBeanFactory.SCOPE_SINGLETON
    SCOPE_PROTOTYPE = ConfigurableBeanFactory.SCOPE_PROTOTYPE
    ROLE_APPLICATION = 0
    ROLE_SUPPORT = 1
    ROLE_INFRASTRUCTURE = 2
