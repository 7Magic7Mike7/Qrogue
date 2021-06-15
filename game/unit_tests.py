
from game.player import *
from game.instruction import *

def defend_unit_test(iterations: int = 1000):
    attributes = PlayerAttributes()
    attributes.set_num_of_qubits(2)
    attributes.set_num_of_cols(5)
    player = Player(attributes)
    player.use_instruction(Instruction(HGate(), qargs=[0], cargs=[]))
    player.use_instruction(Instruction(HGate(), qargs=[1], cargs=[]))
    map0 = { 0: 0, 1: 0 }
    map1 = { 0: 0, 1: 0 }
    for i in range(iterations):
        result = player.defend(i)
        map0[result[0]] += 1
        map1[result[1]] += 1
    print("map0 = ", map0)
    print("map1 = ", map1)

    player.use_instruction(Instruction(HGate(), qargs=[0], cargs=[]))
    player.use_instruction(Instruction(HGate(), qargs=[1], cargs=[]))
    player.print()
    map0 = {0: 0, 1: 0}
    map1 = {0: 0, 1: 0}
    for i in range(iterations):
        result = player.defend(i)
        map0[result[0]] += 1
        map1[result[1]] += 1
    print("map0 = ", map0)
    print("map1 = ", map1)


def print_interface(input_pool_mapper: "list of strings"):
    string = ""
    last = len(input_pool_mapper) - 1
    for i in range(last):
        string += f"{i}... {input_pool_mapper[i]}Gate, "
    string += f"{last}... {input_pool_mapper[last]}Gate"
    print(string)
    print("Greater numbers will do nothing, non-numbers will end the Game!")

