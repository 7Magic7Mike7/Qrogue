from game.actors.factory import EnemyFactory, FightDifficulty, DummyFightDifficulty
from game.actors.enemy import Enemy as EnemyActor
from game.actors.boss import Boss as BossActor
from game.actors.player import Player as PlayerActor, PlayerAttributes, Backpack
from game.actors.riddle import Riddle
from game.callbacks import OnWalkCallback, CallbackPack
from game.collectibles.collectible import ShopItem
from game.collectibles.pickup import Coin, Key
from game.logic.instruction import CXGate, HGate, XGate
from game.logic.qubit import StateVector, DummyQubitSet
from game.map import tiles
from game.map.navigation import Coordinate, Direction
from game.map.rooms import Room, SpawnRoom, GateRoom, WildRoom, BossRoom, ShopRoom, RiddleRoom, Hallway
from util.config import ColorConfig as CC
from util.help_texts import HelpText, HelpTextType

from widgets.my_popups import Popup, CommonPopups


class TutorialPlayer(PlayerActor):
    def __init__(self):
        super(TutorialPlayer, self).__init__(PlayerAttributes(DummyQubitSet()), Backpack(content=[HGate(), XGate()]))


class TutorialDifficulty(FightDifficulty):
    def __init__(self):
        super().__init__(2, [Coin(3)])


class TutorialEnemy(EnemyActor):
    def __init__(self, target: StateVector, reward: tiles.Collectible):
        super().__init__(target, reward, flee_chance=0.0)

    def get_img(self):
        return "E"


class TutorialRiddle(Riddle):
    def __init__(self):
        target = StateVector([0.5, -0.5, 0.5, -0.5])
        reward = CXGate()
        super().__init__(target, reward, attempts=7)


class TutorialBoss(BossActor):
    def __init__(self):
        target = StateVector([0.707 + 0j, 0, 0, 0.707 + 0j])
        super().__init__(target, Coin(11))

    def get_img(self):
        return "B"


class TutorialEnemyFactory(EnemyFactory):
    def __init__(self, start_fight_callback: OnWalkCallback):
        self.__difficulty = TutorialDifficulty()
        super().__init__(start_fight_callback, self.__difficulty)

        self.__reward_index = 0
        self.__enemy_data = [
            (StateVector([0, 0, 1, 0]), Coin(2)),
            (StateVector([0.707 + 0j, 0.707 + 0j, 0, 0]), Key()),
            (StateVector([0, 0, 1, 0]), Coin(1)),
            (StateVector([0.707 + 0j, 0, 0.707 + 0j, 0]), Coin(4)),
            (StateVector([0, 1, 0, 0]), Coin(3)),
            (StateVector([1, 0, 0, 0]), Coin(2)),
        ]

    def get_enemy(self, player: PlayerActor, flee_chance: float) -> EnemyActor:
        data = self.__enemy_data[self.__reward_index]
        enemy = TutorialEnemy(data[0], data[1])
        self.__reward_index = (self.__reward_index + 1) % len(self.__enemy_data)
        return enemy


class TutorialTile(tiles.Message):
    def __init__(self, popup: Popup, id: int, is_active_callback: "bool(int)", progress_callback: "()" = None,
                 blocks: bool = False):
        super().__init__(popup, popup_times=1)
        self.__id = id
        self.__is_active = is_active_callback
        self.__progress = progress_callback
        self.__blocks = blocks

    def get_img(self):
        if self.is_active():
            return super(TutorialTile, self).get_img()
        else:
            if self.__blocks:
                return "X"
            else:
                return self._invisible

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        if self.__blocks:
            if self.is_active():
                return super(TutorialTile, self).is_walkable(direction, player)
            else:
                CommonPopups.TutorialBlocked.show()
                return False
        return super(TutorialTile, self).is_walkable(direction, player)

    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        if self.is_active():
            super(TutorialTile, self).on_walk(direction, player)
            self.__blocks = False  # TutorialTiles should no longer affect the Player after they were activated
            if self.__progress is not None:
                self.__progress()

    def is_active(self):
        return self.__is_active(self.__id)


class CustomWildRoom(Room):
    def __init__(self, east_hallway: Hallway, west_hallway: Hallway,
                 start_fight_callback: "void(EnemyActor, Direction, PlayerActor)", tutorial_tile: TutorialTile,
                 blocking_tile: TutorialTile):
        factory = TutorialEnemyFactory(start_fight_callback)
        self.__enemies = []
        for i in range(Room.INNER_WIDTH):
            self.__enemies.append(tiles.Enemy(factory, self.get_entangled_tiles, id=1, amplitude=1))
        tile_dic = {
            Coordinate(0, Room.MID_Y - 1): tutorial_tile,
            Coordinate(2, Room.INNER_HEIGHT - 2): tiles.Enemy(factory, self.get_entangled_tiles, id=0, amplitude=0),
            Coordinate(3, 0): tiles.Enemy(factory, self.get_entangled_tiles, id=0, amplitude=1),
            Coordinate(Room.INNER_WIDTH - 1, Room.MID_Y - 1): blocking_tile
        }
        for i in range(len(self.__enemies)):
            tile_dic[Coordinate(1, i)] = self.__enemies[i]
        tile_list = Room.dic_to_tile_list(tile_dic)
        super().__init__(tile_list, east_hallway=east_hallway, west_hallway=west_hallway)

    def get_entangled_tiles(self, id: int) -> "list of EnemyTiles":
        if id == 0:
            return []
        return self.__enemies

    def abbreviation(self) -> str:
        return "cWR"


class CustomWildRoom2(WildRoom):
    def __init__(self, factory: EnemyFactory, chance: float = 0.4, north_hallway: Hallway = None,
                 east_hallway: Hallway = None, south_hallway: Hallway = None, west_hallway: Hallway = None):
        super().__init__(factory, chance, north_hallway, east_hallway, south_hallway, west_hallway)
        special = CC.highlight_word("special")
        doors = CC.highlight_object("Doors")
        entangled = CC.highlight_word("entangled")
        enemy = CC.highlight_object("Enemy")
        groups = CC.highlight_word("groups")
        opposite = CC.highlight_word("opposite")
        open = CC.highlight_word("open")
        closed = CC.highlight_word("closed forever")
        boss = CC.highlight_object("Boss")
        text = f"In this Room are two {doors} with a {special} property: they are {entangled}. You already heard " \
               f"about this phenomenon when you were introduced to {enemy} {groups}. But instead of behaving equally " \
               f"the {doors} behave the exact {opposite} - if you {open} one of them the other will be {closed}. " \
               f"But in this Dungeon it is not obligatory to go into one of the rooms behind these {doors}...\n" \
               f"...because the {boss} is already waiting for you in the North."
        self._set_tile(tiles.Message(Popup("Tutorial: Entangled Doors", text, show=False)), 0, Room.MID_Y)

    def abbreviation(self) -> str:
        return "cWR2"


class TutorialGateRoom(GateRoom):
    def __init__(self, hallway: Hallway, tutorial_tile):
        tile_dic = {
            Coordinate(Room.MID_X - 1, 0): tutorial_tile
        }
        super().__init__(hallway, False, tile_dic)


class TutorialBossRoom(BossRoom):
    def __init__(self, hallway: Hallway, start_boss_fight: "(Player, Boss, Direction)"):
        riddle = CC.highlight_object("Riddle")
        gate = CC.highlight_object("Gate")
        shop = CC.highlight_object("Shop")
        helpful = CC.highlight_word("helpful")
        boss = CC.highlight_object("Boss")
        hint = tiles.Message(Popup("Hint:", f"Solving the {riddle} or buying the {gate} from the {shop} might be pretty"
                                            f" {helpful} in defeating the {boss}. Of course you can try it nonetheless "
                                            "but if I were you I'd better use every help I can get.", show=False), -1)
        super().__init__(hallway, True, tiles.Boss(TutorialBoss(), start_boss_fight),
                         tile_dic={Coordinate(1, Room.INNER_HEIGHT - 2): hint})


class Tutorial:
    __SHOW_PAUSE_TUTORIAL = False

    @staticmethod
    def show_pause_tutorial() -> bool:
        if Tutorial.__SHOW_PAUSE_TUTORIAL:
            Tutorial.__SHOW_PAUSE_TUTORIAL = False
            return True
        return False

    def __init__(self):
        Tutorial.__SHOW_PAUSE_TUTORIAL = True
        self.__cur_id = 0
        self.__fight = None
        self.__showed_fight_tutorial = False
        self.__riddle = None
        self.__showed_riddle_tutorial = False
        self.__shop = None
        self.__showed_shop_tutorial = False

    def is_active(self, id: int) -> bool:
        return self.__cur_id == id

    def should_block(self, id: int) -> bool:
        return self.__cur_id > id

    def progress(self):
        self.__cur_id += 1

    def fight(self, player: PlayerActor, enemy: EnemyActor, direction: Direction):
        self.__fight(player, enemy, direction)
        if not self.__showed_fight_tutorial:
            Popup("Tutorial: Fight", HelpText.get(HelpTextType.Fight))
            self.__showed_fight_tutorial = True

    def riddle(self, player: PlayerActor, riddle: Riddle):
        self.__riddle(player, riddle)
        if not self.__showed_riddle_tutorial:
            Popup("Tutorial: Riddle", HelpText.get(HelpTextType.Riddle))
            self.__showed_riddle_tutorial = True

    def shop(self, player: PlayerActor, items: "list of ShopItems"):
        self.__shop(player, items)
        if not self.__showed_shop_tutorial:
            Popup("Tutorial: Shop", HelpText.get(HelpTextType.Shop))
            self.__showed_shop_tutorial = True

    def boss_fight(self, player: PlayerActor, boss: BossActor, direction: Direction):
        self.__boss_fight(player, boss, direction)
        Popup("Tutorial: Boss Fight", HelpText.get(HelpTextType.BossFight))

    def build_tutorial_map(self, player: tiles.Player, cbp: CallbackPack) -> "Room[][], Coordinate":
        self.__fight = cbp.start_fight
        self.__boss_fight = cbp.start_boss_fight
        self.__riddle = cbp.open_riddle
        self.__shop = cbp.visit_shop
        w = [CC.highlight_object("Gate"), CC.highlight_object("Circuit"), CC.highlight_word("locked"),
             CC.highlight_object("Enemies"), CC.highlight_object("Key"), CC.highlight_word("number"),
             CC.highlight_word("group"), CC.highlight_word("entangled"), CC.highlight_word("all others will too"),
             CC.highlight_word("zeros are different"), CC.highlight_word("no group"),
             CC.highlight_word("stepping onto it"), CC.highlight_tile("c"), CC.highlight_word("groups"),
             CC.highlight_object("Boss"), CC.highlight_object("Shop"), CC.highlight_object("Riddle")]
        enemy = CC.highlight_object("Enemy")
        messages = [
            f"Great! The room you're about to enter gives you a new {w[0]} you can use for your "
            f"{w[1]}. But it seems to be {w[2]}...",

            f"Beware! In the next room are some wild {w[3]}. Oh, but maybe one of them has a "
            f"{w[4]}?",

            f"The numbers are {w[3]}! The {w[5]} indicates the {w[6]} they belong to. In a group their behaviour is "
            f"{w[7]}: \n"
            f"If one member runs away when you challenge them, {w[8]}. But if they decide to fight you...\n"
            f"Well, luckily the {w[9]}. They are in {w[10]} and only care about themselves.\n"
            f"Now go ahead and challenge an {enemy} by {w[11]}.",

            f"Nice! Next step onto the {w[12]} and collect your new {w[0]}.\n"
            "Afterwards go to the rooms on the right you haven't visited yet.",

            f"Alright, now comes a room with real {w[3]}. Remember what you were told about the {w[13]} if you want "
            f"to survive!\n"
            f"To the South of it is the {w[15]} and "
            f"North a {w[16]} that gives you a nice reward if you can solve it. Going West takes you one step closer "
            f"to the {w[14]}\n"
            "Good Luck!",
        ]
        popups = [Popup(f"Tutorial #{i + 1}", messages[i], show=False)
                  for i in range(len(messages))]

        entangled_east = tiles.EntangledDoor(Direction.East)
        entangled_south = tiles.EntangledDoor(Direction.South)
        tiles.EntangledDoor.entangle(entangled_east, entangled_south)
        # hallways
        spawn_hallway_east = Hallway(tiles.Door(Direction.East))
        spawn_hallway_south = Hallway(tiles.Door(Direction.South, locked=True))
        cwr_hallway_east = Hallway(tiles.Door(Direction.East))
        riddle_hallway = Hallway(tiles.Door(Direction.South))
        shop_hallway = Hallway(tiles.Door(Direction.North))
        cwr2_hallway_west = Hallway(tiles.Door(Direction.West))
        cwr2_hallway_north = Hallway(tiles.Door(Direction.North))
        cwr2_hallway_east = Hallway(entangled_east)
        cwr2_hallway_south = Hallway(entangled_south)

        spawn_dic = {
            Coordinate(Room.MID_X - 1, Room.INNER_HEIGHT - 1): TutorialTile(popups[0], 0, self.is_active,
                                                                            self.progress),
            Coordinate(Room.INNER_WIDTH - 1, Room.MID_Y - 1): TutorialTile(popups[1], 1, self.is_active, self.progress,
                                                                           blocks=True)
        }
        spawn = SpawnRoom(player, spawn_dic, east_hallway=spawn_hallway_east, south_hallway=spawn_hallway_south)
        spawn_x = 0
        spawn_y = 1
        width = 5
        height = 5
        factory = EnemyFactory(cbp.start_fight, DummyFightDifficulty())

        rooms = [[None for x in range(width)] for y in range(height)]
        rooms[spawn_y][spawn_x] = spawn
        rooms[1][1] = CustomWildRoom(cwr_hallway_east, spawn_hallway_east, self.fight,
                                     TutorialTile(popups[2], 2, self.is_active, self.progress),
                                     TutorialTile(popups[4], 4, self.is_active, self.progress, blocks=True))
        rooms[2][0] = TutorialGateRoom(spawn_hallway_south, TutorialTile(popups[3], 3, self.is_active, self.progress))
        rooms[1][2] = WildRoom(factory, chance=0.8, west_hallway=cwr_hallway_east, north_hallway=riddle_hallway,
                               south_hallway=shop_hallway, east_hallway=cwr2_hallway_west)
        rooms[0][2] = RiddleRoom(riddle_hallway, True, TutorialRiddle(), self.riddle)
        rooms[2][2] = ShopRoom(shop_hallway, False, [ShopItem(Key(2), 3), ShopItem(Key(1), 2), ShopItem(CXGate(), 15)],
                               self.shop)
        rooms[1][3] = CustomWildRoom2(factory, chance=0.7, north_hallway=cwr2_hallway_north,
                                      east_hallway=cwr2_hallway_east, south_hallway=cwr2_hallway_south,
                                      west_hallway=cwr2_hallway_west)
        rooms[0][3] = TutorialBossRoom(cwr2_hallway_north, self.boss_fight)
        rooms[1][4] = WildRoom(factory, chance=0.5, west_hallway=cwr2_hallway_east)
        rooms[2][3] = WildRoom(factory, chance=0.6, north_hallway=cwr2_hallway_south)

        return rooms, Coordinate(spawn_x, spawn_y)
