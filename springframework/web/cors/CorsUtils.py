from abc import ABC, abstractclassmethod
from springframework.utils.mock.inst import (
    HttpServletRequest,
    HttpServletResponse,
)


class CorsUtils:
    @classmethod
    def is_pre_flight_request(
        cls, httpServletRequest: HttpServletRequest
    ) -> bool:
        return False
