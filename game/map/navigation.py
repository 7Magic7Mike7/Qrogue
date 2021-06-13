
class Coordinate:
    def __init__(self, x: int, y: int):
        self.__x = x
        self.__y = y

    def resolve(self):
        return self.__x, self.__y

#enum Direction: