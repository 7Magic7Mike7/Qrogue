from game.actors import robot
from util.config import PathConfig, Config
from util.logger import Logger


class SaveData:
    __NUMBER_OF_SAVE_FILES = 7    # how many save files can be present before we delete the oldest one  # todo maybe move to Config?
    SAVE_NAME = "qrogue-save"

    def __init__(self):
        path = PathConfig.find_latest_save_file()
        #content = ""
        #try:
        #    content = PathConfig.read(path, True)
        #except FileNotFoundError:
        #    Logger.instance().error(NotImplementedError("This line should not be reachable! Please send us the log "
        #                                                "files so we can fix the issue as soon as possible. Thank you!"))
        # todo parse content
        self.__expeditions_finished = 0
        self.__available_robots = [
            robot.LukeBot(),
            robot.NilsBot(),
        ]

    def played_tutorial(self) -> bool:
        return self.__expeditions_finished <= 0 and Config.debugging()

    def available_robots(self) -> iter:
        return iter(self.__available_robots)

    def get_robot(self, index: int) -> robot.Robot:
        if 0 <= index < len(self.__available_robots):
            return self.__available_robots[index]
        return None

    def save(self):
        data = ""
        PathConfig.new_save_file(data)
