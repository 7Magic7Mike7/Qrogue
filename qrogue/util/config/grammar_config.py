# stores constants used in grammar files


class MapGrammarConfig:
    @staticmethod
    def name_prefix() -> str:
        return "Name = "

    @staticmethod
    def description_prefix() -> str:
        return "Description = "


class PuzzleGrammarConfig:
    @staticmethod
    def boss_code() -> str:
        return "code"
