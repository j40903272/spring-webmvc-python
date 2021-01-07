from abc import ABC, abstractmethod


class InitializingBean(ABC):
    @abstractmethod
    def after_properties_set(self) -> None:
        raise NotImplementedError
