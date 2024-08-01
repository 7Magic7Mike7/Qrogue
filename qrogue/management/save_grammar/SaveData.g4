grammar SaveData;

import QrogueBasics;

start : HEADER date_time inventory? gates levels unlocks achievements ENDER;

date_time : DATE TIME ;
duration : value DURATION_UNIT ;

inventory : INVENTORY_HEADER QUANTUM_FUSER value ;

gates : GATES_HEADER gate* ;
gate : NAME_STD ;   // maybe add "amount" later

levels : LEVELS_HEADER level* ;
level : NAME_SPECIAL '@' date_time duration score ;
score : 'Score' '=' value ;
value : VALUE ;

unlocks : UNLOCKS_HEADER unlock* ;
unlock : NAME_STD '@' date_time ;

achievements : ACHIEVEMENTS_HEADER achievement* ;
achievement : NAME_STD '@' date_time score 'out' 'of' value ;

INVENTORY_HEADER : '[INVENTORY]' ;
GATES_HEADER : '[GATES]' ;
LEVELS_HEADER : '[LEVELS]' ;
UNLOCKS_HEADER : '[UNLOCKS]' ;
ACHIEVEMENTS_HEADER : '[ACHIEVEMENTS]' ;

QUANTUM_FUSER : 'QuantumFuser' ;
DURATION_UNIT : 'seconds' ;

DATE : DIGIT DIGIT 'd' DIGIT DIGIT 'm' DIGIT DIGIT DIGIT DIGIT 'y' ;
TIME : DIGIT DIGIT ':' DIGIT DIGIT ':' DIGIT DIGIT ;
VALUE : DIGIT | DIGIT DIGIT | INTEGER ;     // we cannot simply use multiple digits because HALLWAY_ID can be (DIGIT DIGIT)

NAME_STD : CHARACTER+ ;
NAME_SYMBOL : CHARACTER | DIGIT ;
NAME_SPECIAL : CHARACTER NAME_SYMBOL* ;
