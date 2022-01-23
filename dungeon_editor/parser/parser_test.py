
from dungeon_editor.parser.QrogueGrammarListener import TextBasedDungeonGenerator
from game.actors.robot import Testbot
from game.callbacks import CallbackPack
from util.my_random import RandomManager


def start_gp(map):
    print("started game")


def start_fight(**kwargs):
    pass


def generation_test(text: str):
    RandomManager(7)
    t = Testbot(7)
    cbp = CallbackPack(start_gp, start_fight, start_fight, start_fight, start_fight)

    generator = TextBasedDungeonGenerator(7)
    generator.generate(t, cbp, text)


data = \
"""
Qrogue<

[Layout]
~~~~~~~~~~~~~~~~~~~~~~~~
| aa == ab == aa .. ml .. __ .. mr |
| ..    ==    ..    == ..    .. == |
| __ .. SR .. __ .. ma .. mm .. ma |
| ..    ==    ..    ==    ..    == |
| __ .. aa .. oo .. ma .. __ .. ma |
~~~~~~~~~~~~

[Custom Rooms]
aa (Wild):
#############
# 0 1 2 1   #
# c     9   #
# 1   1 3   #
# 2 4   4   #
# 9 1 3 1   #
#############
c *key 2 
0 *stv *rewards

ab (Wild):
#############
# 1 1 2 1   #
# c     2   #
# 2   1 3   #
# 2 2 t 4   #
# 1 1 4 1   #
#############
c *coin 5; t *8093 

ac (Wild):
#############
# 1 1 r 1 _ #
# c _ _ 2   #
# $ _ 1 3   #
# _ _ _ _   #
# c 1 4 c   #
#############
c *coin 5; t *8093 		// nothing happens if we specify a trigger that is not used
r [1, -0, +0, 0j] *hp
$ *mixedPool 3
c *key 1

oo (visible Wild):
# _ #
# _ #
# _ _ 0 #
# _ #
# _ #

ma (visible Gate):
#############
# _ _ 1     #
# _ _ 1     # 
# _ _ 1     #
# _ _ 1     #
# _ _ c     #
#############

ml (visible Shop):
#############
# _ _ $     #
# _ _ 1 1   # 
# _ _ 1 1   #
# _ _ 1   1 #
# _ _ 1   1 #
#############

mm (visible Riddle):
#############
# 1 _ _ _ 1 #
# 1 _ _ _ 1 # 
# _ 1   1   #
# _ 1 _ 1   #
# _ _ r     #
#############

mr (visible Shop):
#############
# _ _ $     #
# _ 1 1     # 
# _ 1 1     #
# 1 _ 1     #
# 1 _ 1     #
#############


[Hallways]
01 (locked; ; )

[StateVector Pools]
custom
*stvPool [ [0j, -0j, -1j, +0], [0.5, -.5j, +.5, 0.5j ] ];  
            default rewards: random *mixedPool

default random [ [.707, +0, -0 + 4j, .707j] ]

[Reward Pools]
custom 
*firstPool [key 22, coin 3]
*mixedPool [ key 2, coin 3 ]

default ordered *firstPool

>Qrogue

"""
generation_test(data)
