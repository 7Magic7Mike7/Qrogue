from typing import Optional


class ErrorConfig:
    @staticmethod
    def singleton(singleton: str) -> str:
        return f"The class \"{singleton}\" is a singleton!"

    @staticmethod
    def singleton_no_init(singleton: str) -> str:
        return f"The singleton \"{singleton}\" has not been initialized yet!"

    @staticmethod
    def singleton_reset(singleton: str) -> str:
        return f"Can only reset the singleton \"{singleton}\" during testing!"

    @staticmethod
    def invalid_map(map_name: str, intro_text: Optional[str] = None) -> str:
        if intro_text is None:
            intro_text = f"Could not find map \"{map_name}\"! "
        return intro_text + "Please download the game files again.\n" \
                            "If this error still occurs but you're sure that the corresponding file is present:"

    @staticmethod
    def qubit_overflow(actual_qubits: int, available_qubits: int) -> str:
        return f"Cannot place a gate with {actual_qubits} qubits on a circuit with only {available_qubits} qubit!\n" \
               f"Please press \"Cancel\" to abort placement."

    @staticmethod
    def raise_deletion_exception():
        """
        Raises a common exception to indicate that this is old code that needs to be removed and worked around.

        Returns: None

        """
        raise Exception("No longer usable!")
