from abc import abstractmethod
from typing import Callable, Any, Optional

from qrogue.game.logic import Message as LogicalMessage
from qrogue.game.logic.actors import Controllable, Riddle, Challenge
from qrogue.game.logic.collectibles import Collectible as LogicalCollectible, Energy as LogicalEnergy, \
    Score as LogicalScore, CollectibleType
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.game.world.tiles.tiles import Tile, TileCode
from qrogue.util import Logger, ColorConfig, CommonQuestions, MapConfig, Config, CommonPopups


class WalkTriggerTile(Tile):
    __show_explanation: Callable[[LogicalMessage, bool], None] = None

    @staticmethod
    def set_show_explanation_callback(show_explanation_callback: Callable[[LogicalMessage, bool], None]):
        WalkTriggerTile.__show_explanation = show_explanation_callback

    @staticmethod
    def _show_explanation(msg: LogicalMessage, overwrite: bool = False):
        if WalkTriggerTile.__show_explanation:
            WalkTriggerTile.__show_explanation(msg, overwrite)
        else:
            Logger.instance().error("WalkTriggerTile's show_explanation is None!", show=False, from_pycui=False)

    def __init__(self, code: TileCode):
        super().__init__(code)
        self.__explanation = None
        self.__event_id = None
        self.__trigger_event = None

    @property
    def has_explanation(self) -> bool:
        return self.__explanation is not None

    @property
    def _explanation(self) -> LogicalMessage:
        return self.__explanation

    @property
    def _event_id(self) -> str:
        return self.__event_id

    def _explicit_trigger(self) -> Any:
        if self.__trigger_event and self.__event_id:
            return self.__trigger_event(self.__event_id)

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True

    def copy(self) -> "Tile":
        tile_copy = self._copy()
        if self.has_explanation:
            tile_copy.set_explanation(self.__explanation)
        if self.__event_id:
            tile_copy.set_event(self.__event_id)
        return tile_copy

    def set_explanation(self, message: LogicalMessage):
        self.__explanation = message

    def set_event(self, event_id: str):
        if self.__event_id is not None:
            Config.check_reachability("WalkTriggerTile.set_event()")
        self.__event_id = event_id

    def trigger(self, direction: Direction, controllable: Controllable, trigger_event_callback: Callable[[str], Any]) \
            -> Any:
        self.__trigger_event = trigger_event_callback
        event_trigger_allowed = self._on_walk(direction, controllable)
        if self.has_explanation:
            WalkTriggerTile._show_explanation(self.__explanation)
            self.__explanation = None  # only display once
        if event_trigger_allowed:
            return self._explicit_trigger()

        return None

    @abstractmethod
    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        """
        Event that is triggered when an actor moves onto this Tile
        :param direction: the Direction from which the actor moves onto this Tile
        :param controllable: the actor (e.g. Player) that is moving onto this Tile
        :return: True if we can trigger an event afterwards, False otherwise
        """
        pass

    @abstractmethod
    def _copy(self) -> "WalkTriggerTile":
        pass


class Trigger(WalkTriggerTile):
    def __init__(self, callback: Callable[[Direction, Controllable], None]):
        super().__init__(TileCode.Trigger)
        self.__callback = callback

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        self.__callback(direction, controllable)
        return True

    def get_img(self):
        return self._invisible

    def _copy(self) -> "Tile":
        return Trigger(self.__callback)


class Teleport(WalkTriggerTile):
    @staticmethod
    def Img() -> str:
        return "t"

    def __init__(self, load_map: Callable[[str, Optional[Coordinate]], None], target_map: str,
                 room: Optional[Coordinate]):
        super().__init__(TileCode.Teleport)
        self.__load_map = load_map
        self.__target_map = target_map
        self.__room = room

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        def callback(confirm: int = 0):
            if confirm == 0:
                self.__load_map(self.__target_map, self.__room)

        if self.__target_map == MapConfig.back_map_string():
            CommonQuestions.GoingBack.ask(callback)
        else:
            CommonQuestions.UseTeleporter.ask(callback)
        return True

    def get_img(self):
        return Teleport.Img()

    def _copy(self) -> "Tile":
        return Teleport(self.__load_map, self.__target_map, self.__room)


class Tunnel(Teleport):
    """
    Like Teleport but locally. So no map is loaded, just the position of the player changes
    """

    def __init__(self, load_room: Callable[[str, Optional[Coordinate]], None], target_room: str,
                 pos: Coordinate):
        super().__init__(load_room, target_room, pos)


class Message(WalkTriggerTile):
    __msg_counter = 0
    __show: Callable[[LogicalMessage, Callable[[], None]], None] = None

    @staticmethod
    def set_show_callback(show_callback: Callable[[LogicalMessage, Callable[[], None]], None]):
        Message.__show = show_callback

    @staticmethod
    def create(text: str, title: str = "Message", popup_times: int = 1) -> "Message":   # todo remove? seems to no longer be in use
        return Message(LogicalMessage.create_with_title(f"Msg_{Message.__msg_counter}", title, text, False, None),
                       popup_times)

    def __init__(self, message: LogicalMessage, popup_times: Optional[int] = 1):
        super().__init__(TileCode.Message)
        self.__message = message
        if popup_times is None or popup_times < 0:
            self.__times: Optional[int] = None  # display "everytime" the controllable steps on it
        else:
            self.__times: Optional[int] = popup_times

    @property
    def _is_showable(self) -> bool:
        if self.__times is None:
            return True    # always show the message
        return self.__times > 0

    def get_img(self):
        if self._is_showable:
            if self.__message.id == "donemsg":
                return TileCode.Goal.representation
            return "."
        else:
            return self._invisible

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        if self._is_showable:
            if self.__times is not None:
                self.__times -= 1
            if Message.__show:
                Message.__show(self.__message, self._explicit_trigger)
            else:
                Logger.instance().error("Message's show is None!", show=False, from_pycui=False)
            return False
        return False

    def _copy(self) -> "Tile":
        message = LogicalMessage.create_from_message(self.__message)
        return Message(message, self.__times)


class Riddler(WalkTriggerTile):
    def __init__(self, open_riddle_callback: Callable[[Controllable, Riddle], None], riddle: Riddle):
        super().__init__(TileCode.Riddler)
        self.__open_riddle = open_riddle_callback
        self.__riddle = riddle
        self.__is_active = True

    @property
    def data(self) -> Optional[int]:
        if self.__is_active:
            return self.__riddle.edits
        else:
            return None

    @property
    def _is_active(self) -> bool:
        if self.__is_active:
            if not self.__riddle.is_active:
                self._explicit_trigger()
                self.__is_active = False
        return self.__is_active

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        if self._is_active:
            self.__open_riddle(controllable, self.__riddle)
        return False

    def get_img(self):
        if self._is_active:
            return TileCode.Riddler.representation
        else:
            return self._invisible

    def _copy(self) -> "Tile":
        return Riddler(self.__open_riddle, self.__riddle)


class Challenger(WalkTriggerTile):
    def __init__(self, open_challenge_callback: Callable[[Controllable, Challenge], None], challenge: Challenge):
        super().__init__(TileCode.Challenger)
        self.__open_challenge = open_challenge_callback
        self.__challenge = challenge
        self.__is_active = True

    @property
    def _is_active(self) -> bool:
        if self.__is_active:
            if not self.__challenge.is_active:
                self._explicit_trigger()
                self.__is_active = False
        return self.__is_active

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        if self._is_active:
            self.__open_challenge(controllable, self.__challenge)
        return False

    def _copy(self) -> "WalkTriggerTile":
        return Challenger(self.__open_challenge, self.__challenge)

    def get_img(self):
        if self._is_active:
            return TileCode.Challenger.representation
        else:
            return self._invisible


class Collectible(WalkTriggerTile):
    __pickup_message: Callable[["Collectible"], None] = None

    @staticmethod
    def set_pickup_message_callback(pickup_message_callback: Callable[[str, str], None],
                                    check_unlocks_callback: Callable[[str], bool]):
        def pickup_message(collectible: LogicalCollectible):
            name = collectible.name()
            desc = collectible.description(check_unlocks_callback)
            pickup_message_callback("Collectible", f"You picked up: {ColorConfig.highlight_object(name)}\n{desc}")

        Collectible.__pickup_message = pickup_message

    def __init__(self, collectible: LogicalCollectible, secret_type: bool = False):
        super().__init__(TileCode.Collectible)
        if collectible is None:
            Logger.instance().warn("Collectible is None!", from_pycui=False)
            collectible = LogicalScore()
        self.__collectible = collectible
        self.__secret_type = secret_type
        self.__active = True

    @property
    def data(self) -> Optional[CollectibleType]:
        if self.__active:
            return self.__collectible.type
        else:
            return None

    def get_img(self):
        if self.__active:
            if self.__secret_type or self.__collectible.type is CollectibleType.Pickup:
                return TileCode.Collectible.representation
            elif self.__collectible.type is CollectibleType.Score:
                return TileCode.CollectibleScore.representation
            elif self.__collectible.type is CollectibleType.Key:
                return TileCode.CollectibleKey.representation
            elif self.__collectible.type is CollectibleType.Gate:
                return TileCode.CollectibleGate.representation
            elif self.__collectible.type is CollectibleType.Qubit:
                return TileCode.CollectibleQubit.representation
            elif self.__collectible.type is CollectibleType.Energy:
                return TileCode.CollectibleEnergy.representation
            else:
                return TileCode.Invalid.representation
        else:
            return self._invisible

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        if self.__active:
            if controllable.give_collectible(self.__collectible):
                if not self.has_explanation:
                    if self.__collectible.type is CollectibleType.Gate:
                        if Collectible.__pickup_message:
                            Collectible.__pickup_message(self.__collectible)
                        else:
                            Logger.instance().error("Collectible's pickup message callback is None!", show=False,
                                                    from_pycui=False)
                self.__active = False
            else:
                CommonPopups.BackpackFull.show()
            return True
        return False

    def _copy(self) -> "Tile":
        return Collectible(self.__collectible)


class Energy(WalkTriggerTile):  # todo why is this extra and not Collectible?
    def __init__(self, amount: int):
        super().__init__(TileCode.Energy)
        self.__amount = amount
        self.__active = True

    @property
    def data(self) -> int:
        return self.__amount

    def get_img(self):
        if self.__active:
            return TileCode.CollectibleEnergy.representation
        else:
            return self._invisible

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        if self.__active:
            controllable.give_collectible(LogicalEnergy(self.__amount))
            self.__active = False
            return True
        return False

    def _copy(self) -> "Tile":
        return Energy(self.__amount)
