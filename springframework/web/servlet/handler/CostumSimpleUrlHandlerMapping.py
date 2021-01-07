import logging
from springframework.web.servlet.handler.SimpleUrlHandlerMapping import (
    SimpleUrlHandlerMapping,
)
from springframework.utils.mock.inst import (
    HttpServletRequest,
    HttpServletResponse,
)


class CustomSimpleUrlHandlerMapping(SimpleUrlHandlerMapping):
    def __init__(self, urlMap: dict(), mockLookupPath: str):
        super().__init__(urlMap)

    # Simply use path info as target path without decoding
    def init_lookup_path(self, request: HttpServletRequest):
        logging.info(f"[request.pathInfo] = {request.pathInfo()}")
        return request.pathInfo()
