from abc import ABC


class MessageSourceResolvable(ABC):
    def get_codes(self):
        return None

    def get_arguments(self):
        return None

    def get_default_message(self):
        return None
