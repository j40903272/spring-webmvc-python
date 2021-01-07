from springframework.beans.factory.config import BeanDefinitionInterface
from springframework.beans.factory.xml import BeanDefinitionParser
from springframework.beans.factory.xml import ParserContext
from xml.etree.ElementTree import Element

# below no implement
# from springframework.beans.factory import BeanDefinitionStoreException
# from springframework.beans.factory.support import BeanDefinitionReaderUtils
# from springframework.beans.factory.config import BeanDefinitionHolder
# from springframework.beans.factory.parsing import BeanComponentDefinition
# from springframework.beans.factory.support import AbstractBeanDefinition
# from springframework.beans.factory.support importBeanDefinitionRegistry


class AbstractBeanDefinitionParser(BeanDefinitionParser):
    def __init__(self):
        self.ID_ATTRIBUTE = "id"
        self.NAME_ATTRIBUTE = "name"

    def parse(
        self, element: Element, parserContext: ParserContext
    ) -> BeanDefinitionInterface:
        definition = self.parseInternal(element, parserContext)
        if (definition is not None) and (not parserContext.isNested()):
            try:
                pass
            except Exception as e:  # BeanDefinitionStoreException
                msg = getattr(e, "message", repr(e))
                parserContext.getReaderContext().error(msg, element)

        return definition

    def resolve_id(self, element, definition, parserContext) -> str:
        if self.shouldGenerateId():
            return parserContext.get_reader_context().generate_bean_name(
                definition
            )
        else:
            Id = getattr(element, "ID_ATTRIBUTE")
            if (not Id) and self.shouldGenerateIdAsFallback():
                Id = parserContext.get_reader_context().generate_bean_name(
                    definition
                )
            return Id

    def register_bean_definition(self, definition, registry):
        # TODO
        # BeanDefinitionReaderUtils.registerBeanDefinition(
        #     definition,
        #     registry
        # )
        pass

    def parse_internal(self, element, parserContext):
        raise NotImplementedError

    def should_generateId(self):
        return False

    def should_generate_id_as_fallback(self):
        return False

    def should_parse_name_as_aliases(self):
        return True

    def should_fire_events(self):
        return True

    def post_process_component_definition(self, componentDefinition):
        pass
