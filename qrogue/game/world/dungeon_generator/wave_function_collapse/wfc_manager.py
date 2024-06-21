import json
from typing import List, Dict, Union, Tuple, Optional

from qrogue.game.world.map.rooms import AreaType
from qrogue.util import PathConfig, MyRandom
from qrogue.util.util_functions import enum_from_str

from .wfc_generator import WFCGenerator, WFCRoomGenerator


class WFCManager:
    __AREA_TYPE_START = "_start"
    __AREA_TYPE_END = "_end"
    __POS_WEIGHTS_START = "pos_weights ="
    __TYPE_WEIGHTS_START = "type_weights = "

    def __init__(self):
        self.__area_data: Dict[AreaType, List[WFCRoomGenerator]] = {}

    def learn(self, templates: Optional[List[Tuple[str, bool]]] = None):
        if templates is None:
            templates = WFCRoomGenerator.get_level_list()
        wr_gen = WFCRoomGenerator.from_level_files(templates, AreaType.WildRoom)
        if AreaType.WildRoom in self.__area_data:
            self.__area_data[AreaType.WildRoom].append(wr_gen)
        else:
            self.__area_data[AreaType.WildRoom] = [wr_gen]

    def store(self, file_name: str):
        data = ""
        for area_type in self.__area_data:
            data += f"{area_type.name}{WFCManager.__AREA_TYPE_START}\n"
            data += f"{len(self.__area_data[area_type])}\n"
            json_strings = []
            for wfc_gen in self.__area_data[area_type]:
                text = f"{WFCManager.__POS_WEIGHTS_START} {WFCGenerator.get_pos_weight_json_string(wfc_gen)}\n"
                text += f"{WFCManager.__TYPE_WEIGHTS_START} {WFCGenerator.get_type_weight_json_string(wfc_gen)}"
                json_strings.append(text)
            data += "; \n".join(json_strings)
            data += "\n"
            data += f"{WFCManager.__AREA_TYPE_END}\n"

        PathConfig.write(file_name, data)

    def load(self, file_name: str):
        data = PathConfig.read(file_name, in_user_path=True)
        line_start = 0
        while line_start < len(data):
            # read area type
            line_end = data.index("\n", line_start)
            area_type = data[line_start:line_end]
            area_type = area_type[:-len(WFCManager.__AREA_TYPE_START)]  # remove meta suffix
            area_type = enum_from_str(AreaType, area_type)

            # read number of upcoming WFCGenerator data (pos and type weights)
            line_start = line_end + 1
            line_end = data.index("\n", line_start)
            num_wfc_gens = int(data[line_start:line_end])

            for i in range(num_wfc_gens):
                line_start = line_end + 1
                json_start = line_start + len(WFCManager.__POS_WEIGHTS_START)
                json_end = data.index(WFCManager.__TYPE_WEIGHTS_START, json_start)
                json_string = data[json_start:json_end]
                pos_weights = json.loads(json_string)

                line_start = json_end + 1
                json_start = line_start + len(WFCManager.__TYPE_WEIGHTS_START)
                if i == num_wfc_gens - 1:
                    json_end = data.index(WFCManager.__AREA_TYPE_END, json_start)
                    json_string = data[json_start:json_end]
                    line_end = json_end + len(WFCManager.__AREA_TYPE_END)
                else:
                    json_end = data.index(WFCManager.__POS_WEIGHTS_START, json_start)
                    json_string = data[json_start:json_end]
                    line_end = json_end
                type_weights = json.loads(json_string)

                # convert json dicts to actual dicts (i.e., correct values instead of strings)
                wfc_gen = WFCRoomGenerator.from_json_dicts(area_type, pos_weights, type_weights)
                if area_type in self.__area_data:
                    self.__area_data[area_type].append(wfc_gen)
                else:
                    self.__area_data[area_type] = [wfc_gen]

            line_start = line_end + 1

    def get_generator(self, area_type: AreaType, selection: Union[int, MyRandom]) -> WFCRoomGenerator:
        if isinstance(selection, int):
            if len(self.__area_data[area_type]) < selection:
                return self.__area_data[area_type][selection]
            else:
                return self.__area_data[area_type][0]   # default value for invalid selection indices
        else:
            return selection.get_element(self.__area_data[area_type], remove=False, msg="WFCManager.get_generator()")
