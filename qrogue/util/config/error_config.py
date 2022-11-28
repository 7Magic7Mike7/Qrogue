

class ErrorConfig:
    @staticmethod
    def singleton(singleton: str) -> str:
        return f"The class \"{singleton}\" is a singleton!"

    @staticmethod
    def singleton_no_init(singleton: str) -> str:
        return f"The singleton \"{singleton}\" has not been initialized yet!"

    @staticmethod
    def singleton_reset(singleton: str) -> str:
        return f"Can only reset the singleton \"{singleton}\" during testing!"
