from abc import ABC, abstractmethod
import sys


class Ordered(ABC):

    HIGHTEST_PRECEDENCE: int = -sys.maxsize
    LOWEST_PRECEDENCE: int = sys.maxsize

    @abstractmethod
    def get_order(self):
        raise NotImplementedError
