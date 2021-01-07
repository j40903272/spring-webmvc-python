from springframework.utils.mock.inst import HttpHeaders, ByteArrayInputStream


class MockPart:

    name: str = None
    filename: str = None
    context: bytes = bytes()
    headers = HttpHeaders()

    def __init__(self, name: str, filename: str = None, content: bytes = None):
        assert name, "'name' must not be empty"
        self.name = name
        self.filename = filename
        self.content = content
        self.headers.setContentDispositionFormData(name, filename)

    def get_name(self) -> str:
        return self.name

    def get_submitted_file_name(self) -> str:
        return self.filename

    def get_content_type(self) -> str:
        contentType = self.headers.get_content_type()
        return None if contentType is None else str(contentType)

    def get_size(self) -> int:
        return len(self.content)

    def get_input_stream(self):
        return ByteArrayInputStream(self.content)

    def write(self, filename: str) -> None:
        raise NotImplementedError

    def delete(self) -> None:
        raise NotImplementedError

    def get_header(self, name: str) -> None:
        return self.headers.getFirst(name)

    def get_headers(self, name: str = None):
        if name is None:
            return self.headers
        headerValues = self.headers.get(name)
        return [] if headerValues is None else headerValues

    def get_header_names(self) -> list:
        return list(self.headers.keys())
