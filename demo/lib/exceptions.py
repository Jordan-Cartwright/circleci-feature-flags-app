class APIException(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class DuplicateFeatureFlagError(Exception):
    def __init__(self, name: str | None = None):
        self.name = name

    def __str__(self) -> str:
        if self.name:
            return f"Feature flag '{self.name}' already exists"
        return "Feature flag already exists"


class FeatureFlagNotFoundError(Exception):

    def __init__(self, flag_id: int | None = None, name: str | None = None):
        self.flag_id = flag_id
        self.name = name

    def __str__(self):
        if self.name:
            return f"Feature flag '{self.name}' not found"
        return f"Feature flag '{self.flag_id}' not found"
