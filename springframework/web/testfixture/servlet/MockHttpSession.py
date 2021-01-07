from datetime import datetime
from springframework.utils.mock.inst import (
    HttpSessionBindingEvent as HttpSessionBindingEvent,
)
from springframework.utils.mock.type import (
    HttpSessionBindingListener,
    Serializable,
)


class MockHttpSession:

    SESSION_COOKIE_NAME: str = "JSESSION"
    nextId: int = 1
    id: str = None
    creationTime: int = int(datetime.now().timestamp())
    maxInactiveInterval: int = None
    lastAccessedTime: int = int(datetime.now().timestamp())
    servletContext = None
    attributes: dict = dict()
    invalid: bool = False
    isNew: bool = True

    def __init__(self, servletContext=None, id: str = None) -> None:
        self.servletContext = servletContext
        if id is None:
            self.id = str(self.nextId)
            self.nextId += 1
        else:
            self.id = id

    def get_creation_time(self) -> int:
        self.assert_is_valid()
        return self.creationTime

    def get_id(self) -> str:
        return self.id

    def change_session_id(self) -> str:
        self.id = str(self.nextId)
        self.nextId += 1
        return self.id

    def access(self) -> None:
        self.lastAccessedTime = int(datetime.now().timestamp())
        self.isNew = False

    def get_last_accessed_time(self) -> int:
        self.assert_is_valid()
        return self.lastAccessedTime

    def get_servlet_context(self):
        self.servletContext

    def set_max_inactive_Interval(self, interval: int) -> None:
        self.maxInactiveInterval = interval

    def get_max_inactive_Interval(self) -> int:
        return self.maxInactiveInterval

    def get_session_context(self):
        raise ValueError("UnsupportedOperationException(getSessionContext")

    def get_attribute(self, name: str):
        self.assert_is_valid()
        assert name is not None, "Attribute name must not be null"
        return self.attributes.get(name)

    def getValue(self, name: str):
        return self.get_attribute(name)

    def get_attribute_names(self) -> list:
        self.assert_is_valid()
        return list(self.attributes.keys())

    def get_value_names(self) -> list:
        self.assert_is_valid()
        return list(self.attributes.keys())

    def set_attribute(self, name: str, value=None) -> None:
        self.assert_is_valid()
        assert name is not None, "Attribute name must not be null"
        if value is None:
            self.remove_attribute(name)
        else:
            oldValue = self.attributes.get(name)
            if oldValue != value:
                if isinstance(oldValue, HttpSessionBindingListener):
                    oldValue.valueUnbound(
                        HttpSessionBindingEvent(self, name, oldValue)
                    )
                if isinstance(value, HttpSessionBindingListener):
                    value.valuebound(
                        HttpSessionBindingEvent(self, name, value)
                    )

    def put_value(self, name: str, value) -> None:
        self.set_attribute(name, value)

    def remove_attribute(self, name: str) -> None:
        self.assert_is_valid()
        assert name is not None, "Attribute name must not be null"
        value = self.attributes.pop(name)
        if isinstance(value, HttpSessionBindingListener):
            value.valueUnbound(HttpSessionBindingEvent(self, name, value))

    def remove_value(self, name: str) -> None:
        self.remove_attribute(name)

    def clear_attributes(self) -> None:
        for name, value in self.attributes.items():
            if isinstance(value, HttpSessionBindingListener):
                value.valuebound(HttpSessionBindingEvent(self, name, value))
        self.attributes.clear()

    def invalidate(self) -> None:
        self.assert_is_valid()
        self.invalid = True
        self.clear_attributes()

    def is_invalid(self) -> bool:
        return self.invalid

    def assert_is_valid(self) -> None:
        assert not self.is_invalid, "The session has already been invalidated"

    def set_new(self, value: bool) -> None:
        self.isNew = value

    def is_new(self) -> bool:
        self.assert_is_valid()
        return self.isNew

    def serialize_state(self):
        state = dict()
        for name, value in self.attributes.items():
            if isinstance(value, Serializable):
                state[name] = value
            elif isinstance(value, HttpSessionBindingListener):
                value.valueUnbound(HttpSessionBindingEvent(self, name, value))

        self.attributes.clear()
        return state

    def deserialize_state(self, state: Serializable) -> None:
        assert isinstance(
            state, dict
        ), "Serialized state needs to be of type [dict]"
        self.attributes.update(state)
