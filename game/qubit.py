

class Qubit:    # TODO introduce interface, for example for only zero_life and one_life qubits
    def __init__(self, index: int, zero_life: int, one_life: int):
        self.index = index
        self.__zero_life = zero_life
        self.__one_life = one_life
        self.__cur_zlife = zero_life
        self.__cur_olife = one_life

    def __str__(self):
        return f"q_{self.index} ({self.__cur_zlife}|{self.__cur_olife})"

    def damage(self, value: int):
        if value == 0:
            self.__cur_zlife -= 1
        else:
            self.__cur_olife -= 1

    def get_zero_life(self):
        return self.__zero_life

    def get_one_life(self):
        return self.__one_life

    def get_cur_life(self):
        return self.__cur_zlife, self.__cur_olife

