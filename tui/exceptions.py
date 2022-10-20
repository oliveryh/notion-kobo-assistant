class Error(Exception):

    pass

class ValidationError(Error):

    def __init__(self, field, message, *args, **kwargs):
        self.field = field
        self.message = message
        super().__init__(*args, **kwargs)