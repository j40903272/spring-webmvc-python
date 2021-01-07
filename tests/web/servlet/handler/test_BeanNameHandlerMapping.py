from unittest import TestCase
from springframework.web.servlet.handler import BeanNameUrlHandlerMapping
from springframework.web.context.support.StaticWebApplicationContext import (
    StaticWebApplicationContext,
)
from springframework.web.testfixture.servlet import MockServletContext


class TestBeanNameUrlHandlerMapping(TestCase):
    def setUp(self):
        self.CONF: str = "/org/springframework/web/servlet/handler/map1.xml"
        self.sc = MockServletContext("")
        self.wac = StaticWebApplicationContext()  # XmlWebApplicationContext
        self.wac.set_servlet_context(self.sc)
        # self.wac.set_config_location(sc)
        self.wac.refresh()

    def test_requests_with_sub_paths(self):
        hm = BeanNameUrlHandlerMapping()
        # hm.set_detect_handlers_in_ancestor_contexts(True)
        hm.set_application_context(self.wac)

    def test_double_mappings(self):
        hm = BeanNameUrlHandlerMapping()
        # TODO
        # hm.register_handler("/mypath/welcome.html", object())
