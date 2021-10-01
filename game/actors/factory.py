from game.actors.enemy import Enemy as EnemyActor, DummyEnemy
from game.callbacks import OnWalkCallback


class EnemyFactory:
    def __init__(self, start_fight_callback: OnWalkCallback):
        self.__start_fight_callback = start_fight_callback

    @property
    def callback(self):
        return self.__start_fight_callback

    def get_enemy(self) -> EnemyActor:
        return DummyEnemy()
