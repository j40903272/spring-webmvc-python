from springframework.web.testfixture.servlet import MockServletContext


# inherit from ServletConfigInterface
class MockServletConfig:

    initParameters = dict()

    def __init__(self, servletContext=None, servletName: str = ""):
        self.servletName = servletName
        if servletContext is None:
            self.servletContext = MockServletContext()
        else:
            self.servletContext = servletContext

    def get_servlet_name(self) -> str:
        return self.servletName

    def get_servlet_context(self) -> str:
        return self.servletContext

    def add_init_parameter(self, name: str, value: str) -> None:
        assert name is not None, "Parameter name must not be null"
        self.initParameters[name] = value

    def get_init_parameter(self, name: str) -> str:
        return self.initParameters.get(name)

    def get_init_parameter_names(self) -> list:
        return self.initParameters.keys()
