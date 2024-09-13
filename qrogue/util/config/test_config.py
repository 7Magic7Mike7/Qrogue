class TestConfig:
    class StateException(Exception):
        def __init__(self, msg: str):
            super(TestConfig.StateException, self).__init__(msg)
            self.__msg = msg

        def __str__(self):
            return f"Qrogue TestStateException: {self.__msg}"

    __IS_ACTIVE = False
    __IS_AUTOMATIC = True

    @staticmethod
    def is_active() -> bool:
        return TestConfig.__IS_ACTIVE

    @staticmethod
    def is_automatic() -> bool:
        return TestConfig.__IS_AUTOMATIC

    @staticmethod
    def automation_step_time() -> int:
        """
        For automated tests the test simulation runs automatically without user intervention.

        :return: how long to wait between each step in ms
        """
        return 10

    @staticmethod
    def key_pause() -> float:
        return 0.05  # time in seconds

    @staticmethod
    def activate():
        TestConfig.__IS_ACTIVE = True

    @staticmethod
    def deactivate():
        TestConfig.__IS_ACTIVE = False

    @staticmethod
    def set_automation(automatic: bool = True):
        TestConfig.__IS_AUTOMATIC = automatic

    @staticmethod
    def test_seed() -> int:
        if TestConfig.is_active():
            return 7
        else:
            raise Exception("TestConfig not yet activated!")
