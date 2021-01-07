class HeaderValueHolder:
    def __init__(self):
        self.values = list()

    def set_value(self, value=None) -> None:
        self.values.clear()
        if value:
            self.values.append(value)

    def add_value(self, value) -> None:
        self.values.append(value)

    def add_values(self, values) -> None:
        self.values.extend(values)

    def add_value_array(self, values) -> None:
        self.values.extend(list(values))

    def get_values(self) -> list:
        return self.values.copy()

    def get_string_values(self) -> list:
        return [str(i) for i in self.values]

    def get_value(self) -> object:
        return self.values[0] if self.values else None

    def get_string_value(self) -> str:
        return str(self.values[0]) if self.values else None

    def __str__(self) -> str:
        return str(self.values)

    def get_by_name(self, headers: dict, name: str):
        assert name, "Header name must not be null"
        for headerName in headers:
            if headerName.casefold() == name:
                return headers.get(headerName)
        return None
