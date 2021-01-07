import os
import logging
import tempfile
from unittest import mock
from springframework.utils.mock.inst import (
    SessionTrackingMode,
    DefaultResourceLoader,
    MediaTypeFactory,
    MediaType,
    Resource,
    RequestDispatcher,
)

from springframework.utils.mock.inst import (
    SessionCookieConfig as MockSessionCookieConfig,
)

# from springframework.web.testfixture.servlet import MockSessionCookieConfig
from springframework.web.testfixture.servlet.MockRequestDispatcher import (
    MockRequestDispatcher,
)


class MockServletContext:

    COMMON_DEFAULT_SERVLET_NAME: str = "default"
    TEMP_DIR_SYSTEM_PROPERTY: str = tempfile.gettempdir()
    DEFAULT_SESSION_TRACKING_MODES = set(
        [
            SessionTrackingMode.COOKIE,
            SessionTrackingMode.URL,
            SessionTrackingMode.SSL,
        ]
    )

    logger = logging.getLogger()
    resourceLoader = None
    resourceBasePath: str = None
    contextPath: str = ""
    contexts = dict()
    majorVersion: int = 3
    minorVersion: int = 1
    effectiveMajorVersion: int = 3
    effectiveMinorVersion: int = 1
    namedRequestDispatchers = dict()
    defaultServletName: str = COMMON_DEFAULT_SERVLET_NAME
    initParameters = dict()
    attributes = dict()
    servletContextName: str = "MockServletContext"
    declaredRoles = set()
    sessionTrackingModes: set = None
    sessionCookieConfig = MockSessionCookieConfig()
    sessionTimeout: int = None
    requestCharacterEncoding: str = None
    responseCharacterEncoding: str = None
    mimeTypes = dict()

    def __init__(
        self, resourceBasePath: str = None, resourceLoader=None
    ) -> None:
        if isinstance(resourceBasePath, str):
            self.resourceBasePath = resourceBasePath
            if resourceLoader is not None:
                self.resourceLoader = resourceLoader
            else:
                self.resourceLoader = DefaultResourceLoader()
        elif resourceBasePath is None:
            self.resourceBasePath = ""
            self.resourceLoader = DefaultResourceLoader()
        else:
            self.resourceBasePath = ""
            self.resourceLoader = resourceBasePath

        self.register_named_dispatcher(
            self.defaultServletName,
            MockRequestDispatcher(self.defaultServletName),
        )

    def get_resource_location(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self.resourceBasePath + path

    def set_context_path(self, contextPath: str) -> None:
        self.contextPath = contextPath

    def get_context_path(self) -> str:
        return self.contextPath

    def register_context(self, contextPath: str, context) -> None:
        self.contexts[contextPath] = context

    def get_context(self, contextPath: str):
        if self.contextPath == contextPath:
            return contextPath
        return self.contexts.get(contextPath)

    def set_major_version(self, majorVersion: int):
        self.majorVersion = majorVersion

    def get_major_version(self) -> int:
        return self.majorVersion

    def set_minor_version(self, minorVersion: int) -> None:
        self.minorVersion = minorVersion

    def get_minor_version(self) -> int:
        return self.minorVersion

    def set_effective_major_version(self, effectiveMajorVersion: int) -> None:
        self.effectiveMajorVersion = effectiveMajorVersion

    def get_effective_major_version(self) -> int:
        return self.effectiveMajorVersion

    def get_mime_type(self, filePath: str) -> str:
        filename, extension = os.path.splitext(filePath)
        if extension in self.mimeTypes:
            return str(self.mimeTypes.get(extension))
        else:
            return str(MediaTypeFactory.getMediaType(filePath))

    def add_mime_type(self, fileExtension: str, mimeType: MediaType) -> None:
        assert fileExtension is not None, "'fileExtension' must not be null"
        self.mimeTypes[fileExtension] = mimeType

    def get_resource_paths(self, path: str) -> set:
        actualPath = path if path.endswith("/") else path + "/"
        resourceLocation = self.get_resource_location(actualPath)
        resource: Resource = None
        try:
            resource = self.resourceLoader.get_resource(resourceLocation)
            file = resource.getFile()
            fileList = file.list()
            if not fileList:
                return None
            resourcePaths = set()
            for fileEntry in fileList:
                resultPath = actualPath + fileEntry
                if resource.createRelative(fileEntry).getFile().isDirectory():
                    resultPath += "/"
                resourcePaths.add(resultPath)
            return resourcePaths

        except IOError as e:
            resource = resource if resource is not None else resourceLocation
            self.logger.warning(
                f"Could not get resource paths for {resource}. {str(e)}"
            )
            return None

    def get_resource(self, path: str):
        resourceLocation = self.get_resource_location(path)
        resource: Resource = None
        try:
            resource = self.resourceLoader.get_resource(resourceLocation)
            if not resource.exists():
                return None
            return resource.getURL()
        except IOError as e:
            resource = resource if resource is not None else resourceLocation
            self.logger.warning(
                f"Could not get URL for resource {resource}. {str(e)}"
            )
            return None

    def get_resource_as_stream(self, path: str):
        resourceLocation = self.get_resource_location(path)
        resource: Resource = None
        try:
            resource = self.resourceLoader.get_resource(resourceLocation)
            if not resource.exists():
                return None
            return resource.getInputStream()
        except IOError as e:
            resource = resource if resource is not None else resourceLocation
            self.logger.warning(
                f"Could not get URL for resource {resource}. {str(e)}"
            )
            return None

    def get_request_dispatcher(self, path: str) -> RequestDispatcher:
        assert path.startswith(
            "/"
        ), f"RequestDispatcher path [ {path} ] at ServletContext level must start with '/'"
        return MockRequestDispatcher(path)

    def get_named_dispatcher(self, path: str) -> RequestDispatcher:
        return self.namedRequestDispatchers.get(path)

    def register_named_dispatcher(
        self, name: str, requestDispatcher: RequestDispatcher
    ) -> None:
        assert name is not None, "RequestDispatcher name must not be null"
        assert (
            requestDispatcher is not None
        ), "RequestDispatcher must not be null"
        self.namedRequestDispatchers[name] = requestDispatcher

    def unregister_named_dispatcher(self, name: str) -> None:
        assert name is not None, "RequestDispatcher name must not be null"
        self.namedRequestDispatchers.pop(name)

    def get_default_servlet_name(self) -> str:
        return self.defaultServletName

    def set_default_servlet_name(self, defaultServletName: str):
        assert (
            defaultServletName
        ), "defaultServletName must not be null or empty"
        self.unregister_named_dispatcher(self.defaultServletName)
        self.defaultServletName = defaultServletName
        self.register_named_dispatcher(
            defaultServletName, MockRequestDispatcher(defaultServletName)
        )

    def get_servlet(self, name: str):
        return None

    def get_servlets(self) -> list:
        return list()

    def get_servlet_names(self) -> list:
        return list()

    def log(self, message: str) -> None:
        self.logger.info(message)

    def get_real_path(self, path: str) -> str:
        resourceLocation = self.get_resource_location(path)
        resource: Resource = None
        try:
            resource = self.resourceLoader.get_resource(resourceLocation)
            return resource.getFile().getAbsolutePath()
        except IOError as e:
            resource = resource if resource is not None else resourceLocation
            self.logger.warning(
                f"Could not determine real path of resource {resource}. {str(e)}"
            )
            return None

    def get_server_info(self) -> str:
        return "MockServletContext"

    def get_init_parameter(self, name: str) -> str:
        assert name is not None, "Parameter name must not be null"
        return self.initParameters.get(name)

    def get_init_parameter_names(self) -> list:
        return list(self.initParameters.keys())

    def set_init_parameter(self, name: str, value: str) -> bool:
        assert name is not None, "Parameter name must not be null"
        if name in self.initParameters:
            return False
        self.initParameters[name] = value
        return True

    def add_init_parameter(self, name: str, value: str) -> None:
        assert name is not None, "Parameter name must not be null"
        self.initParameters[name] = value

    def get_attribute(self, name: str):
        assert name is not None, "Attribute name must not be null"
        return self.attributes.get(name)

    def get_attribute_names(self) -> list:
        return list(self.attributes.keys())

    def set_attribute(self, name: str, value=None) -> None:
        assert name is not None, "Attribute name must not be null"
        if value is not None:
            self.attributes[name] = value
        else:
            self.attributes.pop(name)

    def remove_attribute(self, name: str) -> None:
        assert name is not None, "Attribute name must not be null"
        self.attributes.pop(name)

    def set_servlet_context_name(self, servletContextName: str) -> None:
        self.servletContextName = servletContextName

    def get_servlet_context_name(self) -> str:
        return self.servletContextName

    def get_class_loader(self):
        # TODO
        return mock.MagicMock(name="ClassUtils.getDefaultClassLoader()")

    def declare_roles(self, roleNames: list) -> None:
        assert roleNames is not None, "Role names array must not be null"
        for roleName in roleNames:
            assert roleName, "Role name must not be empty"
            self.declaredRoles.add(roleName)

    def get_declared_roles(self) -> set:
        return set(self.declaredRoles).copy()

    def set_session_tracking_modes(self, sessionTrackingModes: set) -> None:
        self.sessionTrackingModes = sessionTrackingModes

    def get_default_dession_tracking_modes(self) -> set:
        return self.DEFAULT_SESSION_TRACKING_MODES

    def get_effective_session_tracking_modes(self) -> set:
        if self.sessionTrackingModes is None:
            return self.DEFAULT_SESSION_TRACKING_MODES
        return self.sessionTrackingModes

    def get_session_cookie_config(self):
        return self.sessionCookieConfig

    def set_session_timeout(self, sessionTimeout: int) -> None:
        self.sessionTimeout = sessionTimeout

    def get_session_timeout(self) -> int:
        return self.sessionTimeout

    def set_request_character_rncoding(
        self, requestCharacterEncoding: str = None
    ) -> None:
        self.requestCharacterEncoding = requestCharacterEncoding

    def get_request_character_rncoding(self) -> str:
        self.requestCharacterEncoding

    def set_response_character_encoding(
        self, responseCharacterEncoding: str = None
    ) -> None:
        self.responseCharacterEncoding = responseCharacterEncoding

    def get_response_character_encoding(self) -> str:
        return self.responseCharacterEncoding

    # ---------------------------------------------------------------------
    #  Unsupported Servlet 3.0 registration methods
    # ---------------------------------------------------------------------
    # TODO
