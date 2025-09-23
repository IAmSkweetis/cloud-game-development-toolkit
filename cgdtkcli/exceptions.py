class CgdtkException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class CgdtkConfigError(CgdtkException):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class CgdtkConfigFileExistsError(CgdtkConfigError):
    def __init__(self, config_file: str) -> None:
        super().__init__(f"Config file {config_file} already exists.")
