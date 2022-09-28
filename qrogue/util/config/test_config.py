

class TestConfig:
    class StateException(Exception):
        def __init__(self, msg: str):
            super(TestConfig.StateException, self).__init__(msg)
            self.__msg = msg

        def __str__(self):
            return f"Qrogue TestStateException: {self.__msg}"

    __IS_ACTIVE = False

    @staticmethod
    def is_active() -> bool:
        return TestConfig.__IS_ACTIVE

    @staticmethod
    def key_pause() -> float:
        return 0.05     # time in seconds

    @staticmethod
    def activate():
        TestConfig.__IS_ACTIVE = True

    @staticmethod
    def deactivate():
        TestConfig.__IS_ACTIVE = False

