# from springframework.beans.factory.config import BeanDefinitionInterface


class ParserContext:
    def __init__(self, readerContext, delegate, containingBeanDefinition=None):
        self._readerContext = readerContext
        self._delegate = delegate
        self._containingBeanDefinition = containingBeanDefinition
        self._containingComponents = list()  # deque

    def get_reader_context(self):
        return self._readerContext

    def get_registry(self):
        return self._readerContext.get_registry()

    def get_delegate(self):
        return self._delegate

    def get_containing_bean_definition(self):
        return self._containingBeanDefinition

    def is_nested(self):
        return self._containingBeanDefinition is not None

    def is_default_lazy_init(self):
        # TODO
        pass

    def extract_source(self, sourceCandidate):
        return self._readerContext.extract_source(sourceCandidate)

    def get_containing_component(self):
        return self.containingComponents.peek()

    def push_containing_component(self, containingComponent):
        self._containingComponents.push(containingComponent)

    def pop_and_register_containing_component(self, containingComponent):
        self.register_component(self.popContainingComponent())

    def register_component(self, component):
        containingComponent = self.get_containing_component()
        if containingComponent is not None:
            containingComponent.addNestedComponent(component)
        else:
            self._readerContext.fireComponentRegistered(component)

    def registerbean_component(self, component):
        #  TODO
        # BeanDefinitionReaderUtils.registerBeanDefinition(
        #     component,
        #     self.get_registry()
        # )
        self.register_component(component)
