from typing import Optional, Callable, Tuple


class Message:
    __err_count = 0

    @staticmethod
    def error(text: str) -> "Message":
        Message.__err_count += 1
        return Message(f"Error_{Message.__err_count}", "Error", text, False, None, None, None)

    @staticmethod
    def create_with_title(m_id: str, title: str, text: str, priority: bool, position: Optional[int] = None) \
            -> "Message":
        return Message(m_id, title, text, priority, position, None, None)

    @staticmethod
    def create_with_alternative(m_id: str, title: str, text: str, priority: bool, position: int, event: str,
                                alternative: "Message") -> "Message":
        message = Message(m_id, title, text, priority, position, event, alternative.id)
        message.resolve_message_ref(alternative)
        return message

    @staticmethod
    def create_with_exception(m_id: str, title: str, text: str, priority: bool, event: str):
        return Message(m_id, title, text, priority, None, event, "none")

    @staticmethod
    def create_from_message(message: "Message") -> "Message":
        msg = Message(message.__m_id, message.__title, message.__text, message.__priority, message.__position,
                      message.__event, message.__alt_ref)
        if message.__alt_message:
            msg.resolve_message_ref(message.__alt_message)
        return msg

    def __init__(self, m_id: str, title: str, text: str, priority: bool, position: Optional[int], event: Optional[str],
                 alternative: Optional[str]):
        assert position is None or isinstance(position, int), "Invalid position type!"

        self.__m_id = m_id
        self.__title = title
        self.__text = text
        self.__priority = priority
        self.__position = position
        self.__alt_ref = alternative
        self.__event = event
        self.__alt_message = None

        if self.__alt_ref is self.id:
            raise ValueError("Messages must not reference themselves as alternatives!")

    @property
    def id(self) -> str:
        return self.__m_id

    @property
    def priority(self) -> bool:
        return self.__priority

    @property
    def position(self) -> Optional[int]:
        return self.__position

    @property
    def alt_message_ref(self) -> Optional[str]:
        return self.__alt_ref

    def resolve_message_ref(self, message: "Message") -> bool:
        if self.alt_message_ref == message.__m_id:
            # check for cycles
            alt = message
            length = 1
            while alt:
                if alt is self:
                    raise ValueError(f"Found cycle of length {length} in alternative messages!")
                alt = alt.__alt_message
                length += 1
            self.__alt_message = message
            return True
        return False

    def get(self, check_achievement: Callable[[str], bool]) -> Optional[Tuple[str, str]]:
        if self.__event is not None and check_achievement(self.__event):
            if self.alt_message_ref == "none":
                return None
            if self.__alt_message:
                return self.__alt_message.get(check_achievement)
        else:
            return self.__title, self.__text
