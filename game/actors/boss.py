
from abc import abstractmethod
from game.actors.enemy import Enemy
from game.logic.difficulty import DummyDifficulty


class Boss(Enemy):
    @abstractmethod
    def get_reward(self):
        pass


class DummyBoss(Boss):
    def __init__(self):
        #super(DummyBoss, self).__init__(DummyQubitSet(), StateVector([1 / np.sqrt(2), 1 / np.sqrt(2), 0 + 0j, 0 + 0j]))
        super(DummyBoss, self).__init__(DummyDifficulty())

    def get_img(self):
        return "B"

    def get_reward(self):
        print("TODO: give reward")
