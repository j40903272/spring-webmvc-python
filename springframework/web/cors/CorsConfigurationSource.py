from abc import ABC, abstractclassmethod
from springframework.web.cors import CorsConfiguration
from springframework.web.testfixture.servlet import MockHttpServletRequest


class CorsConfigurationSource:
    def get_cors_configuration(
        self, httpservletRequest: MockHttpServletRequest
    ) -> CorsConfiguration:
        return None
