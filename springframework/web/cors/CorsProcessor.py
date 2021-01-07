from abc import ABC, abstractclassmethod
from springframework.web.cors import CorsConfiguration
from springframework.web.testfixture.servlet import MockHttpServletRequest
from springframework.web.testfixture.servlet import MockHttpServletResponse


class CorsProcessor(ABC):
    def process_request(
        self,
        corsConfiguration: CorsConfiguration,
        httpservletRequest: MockHttpServletRequest,
        httpServletResponse: MockHttpServletResponse,
    ) -> bool:
        return True
