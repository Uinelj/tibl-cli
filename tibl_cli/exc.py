class TiblError(Exception):
    pass

class TiblFormatError(TiblError):
    def __init__(self, message):
        self.message = message
    pass

class TiblFileError(TiblError):
    def __init__(self, message):
        self.message = message
    pass

class TiblGitError(TiblError):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

