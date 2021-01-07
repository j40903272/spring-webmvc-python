from abc import ABC, abstractmethod, ABCMeta
from springframework.utils.mock.inst import HttpServletRequest


class HandlerMappingInterfaceMeta(type):
    def __init__(cls, *args, **kwargs):
        cls.BEST_MATCHING_HANDLER_ATTRIBUTE: str = (
            cls.__name__ + ".bestMatchingHandler"
        )
        cls.LOOKUP_PATH: str = cls.__name__ + ".lookupPath"
        cls.PATH_WITHIN_HANDLER_MAPPING_ATTRIBUTE: str = (
            cls.__name__ + ".pathWithinHandlerMapping"
        )
        cls.BEST_MATCHING_PATTERN_ATTRIBUTE: str = (
            cls.__name__ + ".pathWithinHandlerMapping"
        )
        cls.INTROSPECT_TYPE_LEVEL_MAPPING: str = (
            cls.__name__ + ".bestMatchingPattern"
        )
        cls.URI_TEMPLATE_VARIABLES_ATTRIBUTE: str = (
            cls.__name__ + ".introspectTypeLevelMapping"
        )
        cls.MATRIX_VARIABLES_ATTRIBUTE: str = (
            cls.__name__ + ".uriTemplateVariables"
        )
        cls.PRODUCIBLE_MEDIA_TYPES_ATTRIBUTE: str = (
            cls.__name__ + ".matrixVariables"
        )


# https://stackoverflow.com/questions/57349105/python-abc-inheritance-with-specified-metaclass
class CombinedMeta(HandlerMappingInterfaceMeta, ABCMeta):
    pass


class HandlerMappingInterface(ABC, metaclass=CombinedMeta):
    def uses_path_patterns(self) -> bool:
        return False

    @abstractmethod
    def get_handler(self, request: HttpServletRequest):
        raise NotImplementedError
