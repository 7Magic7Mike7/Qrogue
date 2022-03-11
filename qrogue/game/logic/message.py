from typing import Optional, Callable, Tuple

from qrogue.util import Config


class Message:
    __err_count = 0

    @staticmethod
    def error(text: str) -> "Message":
        Message.__err_count += 1
        return Message(f"Error_{Message.__err_count}", "Error", text, None, None)

    @staticmethod
    def create_simple(m_id: str, text: str) -> "Message":
        return Message(m_id, Config.scientist_name(), text, None, None)

    @staticmethod
    def create_with_title(m_id: str, title: str, text: str) -> "Message":
        return Message(m_id, title, text, None, None)

    def __init__(self, m_id: str, title: str, text: str, event: Optional[str], alternative: Optional[str]):
        self.__m_id = m_id
        self.__title = title
        self.__text = text
        self.__alt_ref = alternative
        self.__event = event
        self.__alt_message = None

        if self.alt_message_ref is self.id:
            raise ValueError("Messages must not reference themselves as alternatives!")

    @property
    def id(self) -> str:
        return self.__m_id

    @property
    def alt_message_ref(self) -> str:
        if self.__alt_ref:
            return self.__alt_ref
        else:
            return None

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

    def get(self, check_achievement: Callable[[str], bool]) -> Tuple[str, str]:
        if check_achievement(self.__event):
            if self.__alt_message:
                return self.__alt_message.get(check_achievement)
        else:
            return self.__title, self.__text
