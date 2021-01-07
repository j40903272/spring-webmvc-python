from springframework.beans.factory.config import BeanDefinitionInterface
from springframework.beans.factory.xml import ParserContext
from xml.etree.ElementTree import Element


class BeanDefinitionParser:
    def parse(
        self, element: Element, parserContext: ParserContext
    ) -> BeanDefinitionInterface:
        raise NotImplementedError
