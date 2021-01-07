import logging
from springframework.utils.mock.type import HttpServletResponseWrapper
from springframework.web.testfixture.servlet.MockHttpServletResponse import (
    MockHttpServletResponse,
)


class MockRequestDispatcher:
    logger = logging.getLogger()
    resource: str = None

    def __init__(self, resource: str):
        assert resource is not None, "Resource must not be null"
        self.resource = resource

    def forward(self, request, response) -> None:
        assert request is not None, "Request must not be null"
        assert response is not None, "Response must not be null"
        assert (
            not response.is_committed()
        ), "Cannot perform forward - response is already committed"
        self.get_mock_http_servlet_response(response).set_forwarded_url(
            self.resource
        )

    def include(self, request, response) -> None:
        assert request is not None, "Request must not be null"
        assert response is not None, "Response must not be null"
        self.get_mock_http_servlet_response(response).add_included_url(
            self.resource
        )
        self.logger.debug(
            f"MockRequestDispatcher: including [ {self.resource} ]"
        )

    def get_mock_http_servlet_response(self, response):
        if isinstance(response, MockHttpServletResponse):
            return response
        if isinstance(response, HttpServletResponseWrapper):
            return self.get_mock_http_servlet_response(response.get_response())
        raise ValueError(
            "MockRequestDispatcher requires MockHttpServletResponse"
        )
