from abc import ABC, abstractmethod
from springframework.web.util.pattern import PathPatternParser
from springframework.web.util.pattern import PathPattern
from springframework.web.servlet.handler import RequestMatchResult
from springframework.web.servlet import (
    HandlerMappingInterface as HandlerMapping,
)
from springframework.utils.mock.inst import HttpServletRequest


class MatchableHandlerMapping(HandlerMapping, ABC):
    def get_pattern_parser(self) -> PathPattern:
        return None

    @abstractmethod
    def match(
        self, request: HttpServletRequest, pattern: str
    ) -> RequestMatchResult:
        return None
