
from game.actors.player import *
from game.logic.instruction import *

def defend_unit_test(iterations: int = 1000):
    attributes = PlayerAttributes()
    attributes.set_num_of_qubits(2)
    attributes.set_space(5)
    player = Player(attributes)
    player.use_instruction(HGate(0))
    player.use_instruction(HGate(1))
    map0 = { 0: 0, 1: 0 }
    map1 = { 0: 0, 1: 0 }
    for i in range(iterations):
        result = player.defend(i)
        map0[result[0]] += 1
        map1[result[1]] += 1
    print("map0 = ", map0)
    print("map1 = ", map1)

    player.use_instruction(HGate(0))
    player.use_instruction(HGate(1))
    player.print()
    map0 = {0: 0, 1: 0}
    map1 = {0: 0, 1: 0}
    for i in range(iterations):
        result = player.defend(i)
        map0[result[0]] += 1
        map1[result[1]] += 1
    print("map0 = ", map0)
    print("map1 = ", map1)


def print_interface(input_pool_mapper: "list of str"):
    string = ""
    last = len(input_pool_mapper) - 1
    for i in range(last):
        string += f"{i}... {input_pool_mapper[i]}Gate, "
    string += f"{last}... {input_pool_mapper[last]}Gate"
    print(string)
    print("Greater numbers will do nothing, non-numbers will end the Game!")

