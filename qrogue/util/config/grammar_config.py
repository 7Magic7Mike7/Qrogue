# stores constants used in grammar files


class MapGrammarConfig:
    @staticmethod
    def name_prefix() -> str:
        return "Name = "

    @staticmethod
    def description_prefix() -> str:
        return "Description = "
