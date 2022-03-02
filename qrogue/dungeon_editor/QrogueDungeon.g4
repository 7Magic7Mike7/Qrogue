grammar QrogueDungeon;

// RULES

start  :    HEADER (NAME '=' TEXT)?
            robot layout rooms hallways stv_pools reward_pools messages
            ENDER;

integer : DIGIT | HALLWAY_ID | INTEGER ;
complex_number : SIGN? (IMAG_NUMBER | (integer | FLOAT) (SIGN IMAG_NUMBER)?) ;

robot: ROBOT DIGIT 'qubits' '[' REFERENCE (LIST_SEPARATOR REFERENCE)* ']' ;

// building the layout of the dungeon
layout : LAYOUT HORIZONTAL_SEPARATOR* l_room_row (l_hallway_row l_room_row)* HORIZONTAL_SEPARATOR* ;
l_room_row :    VERTICAL_SEPARATOR
                (ROOM_ID | EMPTY_ROOM)  ((HALLWAY_ID | EMPTY_HALLWAY)   (ROOM_ID | EMPTY_ROOM))*
                VERTICAL_SEPARATOR ;
l_hallway_row : VERTICAL_SEPARATOR
                (HALLWAY_ID | EMPTY_HALLWAY)+
                VERTICAL_SEPARATOR ;

// building the non-template rooms used in the layout (note: template rooms are pre-defined rooms)
rooms : ROOMS room* ;
room : ROOM_ID r_attributes ':' WALL* r_row+ WALL* tile_descriptor* ;
r_attributes : '(' r_visibility r_type ')' ;  // visibile/in sight, type
r_visibility : (VISIBLE_LITERAL | FOGGY_LITERAL)? ;
r_type :    (SPAWN_LITERAL | BOSS_LITERAL | WILD_LITERAL | SHOP_LITERAL | RIDDLE_LITERAL | GATE_ROOM_LITERAL |
            TREASURE_LITERAL) ;
r_row : WALL tile+ WALL ;
tile :  'o' | 't' | 'm' | DIGIT | 'c' | 'e' | 'r' | '$' | '_' ;    // obstacle, trigger, message, enemy, collectible,
                                                                   // energy, riddle, shop, floor

// further describing the tiles used in the room
tile_descriptor : trigger_descriptor | message_descriptor |
                  (enemy_descriptor | collectible_descriptor | energy_descriptor | riddle_descriptor | shop_descriptor)
                  (TUTORIAL_LITERAL REFERENCE)? (TRIGGER_LITERAL REFERENCE)? ;  // winning a fight or picking up a collectible can also trigger an event
trigger_descriptor : 't' REFERENCE ;   // reference to the event to trigger
message_descriptor : 'm' integer REFERENCE ;    // #times displayed, reference to the text that should be shown
enemy_descriptor : DIGIT REFERENCE REFERENCE?;    // enemy, id of statevector pool, id of reward pool
collectible_descriptor : 'c' REFERENCE integer? ; // id of reward pool to draw from, number of rewards to draw (note: template pools like *key provide "normal" collectibles)
energy_descriptor : 'e' integer ;    // amount
riddle_descriptor : 'r' (REFERENCE | stv) (REFERENCE | collectible) ;   // stv pool id, reward pool id
shop_descriptor : '$' (REFERENCE | collectibles) integer ;   // reward pool id or collectible list, num of items to draw


// describing the hallways used in the layout (except for the default one '==')
hallways : HALLWAYS hallway*;
hallway : HALLWAY_ID h_attributes ;
h_attributes : '(' (OPEN_LITERAL | CLOSED_LITERAL | LOCKED_LITERAL | EVENT_LITERAL REFERENCE)
                ('one way' DIRECTION PERMANENT_LITERAL?)?
                ('entangled' '[' HALLWAY_ID (LIST_SEPARATOR HALLWAY_ID)* ']')? ')' ;

// how to draw an element from a pool
draw_strategy : RANDOM_DRAW | ORDERED_DRAW ;    // default is random draw, because mostly we don't want to have to explicitely define it

stv_pools : STV_POOLS ('custom' stv_pool+)? 'default' default_stv_pool ;    // default pools are for enemies without defined pools
default_stv_pool : REFERENCE | draw_strategy? stvs ;
stv_pool : REFERENCE draw_strategy? stvs ('default' 'rewards' ':' REFERENCE)?;     // id of pool, list of statevectors, id of default reward pool
stvs : '[' stv (LIST_SEPARATOR stv)* ']' ;
stv :  '[' complex_number (LIST_SEPARATOR complex_number)* ']';

reward_pools : REWARD_POOLS ('custom' reward_pool+)? 'default' default_reward_pool ;    // default pools are for enemies without defined pools
default_reward_pool : REFERENCE | draw_strategy? collectibles ;      // the default pool can either be an ID or a list of collectibles
reward_pool : REFERENCE draw_strategy? collectibles ;     // id, pool of collectibles
collectibles : '[' collectible (LIST_SEPARATOR collectible)* ']' ;
collectible :   (KEY_LITERAL integer | COIN_LITERAL integer | HEALTH_LITERAL integer | GATE_LITERAL REFERENCE |
                QUBIT_LITERAL integer?) ;

messages : MESSAGES (REFERENCE TEXT)* ;
//message : REFERENCE TEXT ('event' REFERENCE 'alternative' REFERENCE)? ;    // alternative message if a certain event already happened

// TOKEN

// Characters implicitely used for special purposes:
// [ ]      for highlighting headlines and grouping lists
// < >      to mark the beginning and the end of the dungeon
// _        single: Floor-tile | double: to mark the use of predefined template rooms or hallways
// .        double: is used for an empty field in the map layout, in combination with digits or characters as comma for floats or tile descriptor
// =        double: is used for the non-existing hallway
// ~ | #    separators for Layout and Rooms for visual indications
// :        to mark the beginning of a room's content
// + -      signs for numbers
// ;        optical separation, e.g. can be use to separate things without a new line
// *        marks the beginning of a pool id (inspired by pointers)

// general token
DIGIT : [0-9] ;
INTEGER : DIGIT DIGIT DIGIT+ ;
FLOAT : DIGIT? '.' DIGIT+ ;
IMAG_NUMBER : (DIGIT* | FLOAT) 'j' ;
SIGN : PLUS_SIGN | MINUS_SIGN ;
CHARACTER_LOW : [a-z] ;
CHARACTER_UP : [A-Z] ;
CHARACTER : CHARACTER_LOW | CHARACTER_UP ;
TEXT : '"' .*? '"' ;

// literals
VISIBLE_LITERAL : 'visible' ;
FOGGY_LITERAL : 'foggy' ;

OPEN_LITERAL : 'open' ;
CLOSED_LITERAL : 'closed' ;
LOCKED_LITERAL : 'locked' ;
EVENT_LITERAL : 'event' ;
PERMANENT_LITERAL: 'permanent' ;

SPAWN_LITERAL : 'Spawn' ;
WILD_LITERAL : 'Wild' ;
SHOP_LITERAL : 'Shop' ;
RIDDLE_LITERAL : 'Riddle' ;
BOSS_LITERAL : 'Boss' ;
GATE_ROOM_LITERAL : 'Gate' ;
TREASURE_LITERAL : 'Treasure' ;

TUTORIAL_LITERAL : 'tutorial' ;
TRIGGER_LITERAL : 'trigger' ;
KEY_LITERAL : 'key' ;
COIN_LITERAL : 'coin' ;
HEALTH_LITERAL : 'health' ;
GATE_LITERAL : 'gate' ;
QUBIT_LITERAL : 'qubit' ;

PLUS_SIGN : '+' ;
MINUS_SIGN : '-' ;

// headline token
HEADER : 'Qrogue<' ;
ENDER : '>Qrogue' ;
NAME : 'Name' ;
ROBOT : '[Robot]' ;
LAYOUT : '[Layout]' ;
ROOMS : '[Custom Rooms]' ;
HALLWAYS : '[Hallways]' ;
STV_POOLS : '[StateVector Pools]' ;
REWARD_POOLS : '[Reward Pools]' ;
MESSAGES : '[Messages]' ;

// optical separators
HORIZONTAL_SEPARATOR : '~' ;
VERTICAL_SEPARATOR : '|' ;
LIST_SEPARATOR : ',' ;
WALL : '#' ;
EMPTY_HALLWAY : '..' ;
EMPTY_ROOM : '__' ;

// keywords
DIRECTION : 'North' | 'East' | 'South' | 'West' ;
ORDERED_DRAW : 'ordered' ;
RANDOM_DRAW : 'random' ;

// ids
ROOM_ID : ('_' | CHARACTER) CHARACTER ;
HALLWAY_ID : '==' | ('_' | DIGIT) DIGIT ;   // '==' default (closed, no entanglement), same as _1 but with better visuals
REFERENCE : '*' (CHARACTER | DIGIT)+ ;

// ignored characters (whitespace and comments)
WS : [ \t\r\n]+ -> skip ;
UNIVERSAL_SEPARATOR : ';'+ -> skip ;
COMMENT : '/*' .*? '*/' -> skip ;
LINE_COMMENT : '//' ~[\r\n]* -> skip ;