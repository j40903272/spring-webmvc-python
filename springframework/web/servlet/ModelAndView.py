from springframework.web.servlet import View
from springframework.utils.mock.type import HttpStatus
from springframework.utils.mock.inst import ModelMap

# ModelMap important ; need implement


class ModelAndView:

    _view = None
    _model = None
    _status = None
    _cleared = False

    def __init__(self, view=None, arg2=None, arg3=None):
        self._view = view
        if arg2 is not None and arg3 is not None:
            if isinstance(arg2, dict) and arg2:
                self.get_model_map().addAllAttributes(arg2)
            if isinstance(arg2, HttpStatus):
                self._status = arg2
            if isinstance(arg3, HttpStatus):
                self._status = arg3
            if isinstance(arg2, str) and isinstance(arg2, object):
                self.add_object(arg2, arg3)

    def set_view_name(self, viewName: str) -> None:
        self._view = viewName

    def get_view_name(self) -> str:
        return self._view

    def set_view(self, view: View) -> None:
        self._view = view

    def get_view(self) -> View:
        return self._view

    def has_view(self) -> bool:
        return self._view is not None

    def is_reference(self) -> bool:
        return isinstance(self._view, str)

    def get_model_internal(self) -> dict:
        return self._model

    def get_model_map(self):
        if self._model is None:
            self._model = {}  # ModelMap()
        return self._model

    def get_model(self) -> dict:
        return self.get_model_map()

    def set_status(self, status: HttpStatus) -> None:
        self._status = status

    def get_status(self) -> HttpStatus:
        return self._status

    def add_object(self, attributeName: str, attributeValue: object = None):
        if attributeValue is None and isinstance(attributeName, object):
            attributeValue = attributeName
            # self.get_model_map().addAttribute(attributeValue)
            self.get_model_map()[attributeName] = attributeValue
        else:
            # self.get_model_map().addAttribute(attributeName, attributeValue)
            self.get_model_map()[attributeName] = attributeValue
        return self

    def add_all_objects(self, modelMap: dict):
        self.get_model_map().addAllAttributes(modelMap)
        return self

    def clear(self) -> None:
        self._view = None
        self._model = None
        self._cleared = True

    def is_empty(self) -> bool:
        return (self.view is None) and (not self.model)

    def was_cleared(self) -> bool:
        return self._cleared and self.is_empty()

    def __str__(self) -> str:
        return f"ModelAndView [view={self.formatView()}; model={self.model}]"

    def formatView(self) -> str:
        return f'"{self.view}"' if self.is_reference() else "[{self.view}]"
