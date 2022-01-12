grammar QrogueDungeon;

// RULES

start  : HEADER layout rooms hallways stv_pools reward_pools ENDER;

number : DIGIT | HALLWAY_ID | NUMBER ;
imag_number : IMAG_NUMBER ;
complex_number : SIGN? (imag_number | number (SIGN imag_number)?) ;

// building the layout of the dungeon
layout : LAYOUT HORIZONTAL_SEPARATOR* l_room_row (l_hallway_row l_room_row)* HORIZONTAL_SEPARATOR* ;
l_room_row : VERTICAL_SEPARATOR ROOM_ID (HALLWAY_ID ROOM_ID)* VERTICAL_SEPARATOR ;
l_hallway_row : VERTICAL_SEPARATOR (HALLWAY_ID (EMPTY_FIELD HALLWAY_ID)*)? VERTICAL_SEPARATOR ;

// building the non-template rooms used in the layout (note: template rooms are pre-defined rooms)
rooms : ROOMS room* ;
room : ROOM_ID r_attributes ':' WALL* r_row+ WALL* tile_descriptor* ;
r_attributes : '(' r_visibility r_type ')' ;  // visibile/in sight, type
r_visibility : ('visible' | 'foggy')? ;
r_type :  ('Spawn' | 'Boss' | 'Wild' | 'Shop' | 'Riddle' | 'Gate') ;
r_row : WALL tile+ WALL ;
tile : DIGIT | 'c' | 't' | 'e' ;    // enemy, collectible, trigger, energy

// further describing the tiles used in the room
tile_descriptor : (enemy_descriptor | collectible_descriptor | trigger_descriptor | energy_descriptor) ;
enemy_descriptor : DIGIT draw_strategy? POOL_ID (draw_strategy? POOL_ID)?;    // enemy, id of statevector pool, id of reward pool
collectible_descriptor : 'c' draw_strategy? POOL_ID number? ; // id of reward pool to draw from, number of rewards to draw (note: template pools like *key provide "normal" collectibles)
collectible : ('key' number | 'coin' number | 'health' number | 'gate' number) ;
trigger_descriptor : 't' number ;   // id of the event to trigger
energy_descriptor : 'e' number ;    // amount

// describing the hallways used in the layout (except for the default one '==')
hallways : HALLWAYS hallway*;
hallway : HALLWAY_ID h_attributes ;
h_attributes : '(' ('open' | 'closed' | 'locked') ('one way' DIRECTION)? ('entangled' '{' HALLWAY_ID+ '}')? ')' ;

// how to draw an element from a pool
draw_strategy : RANDOM_DRAW | ORDERED_DRAW ;    // default is random draw, because mostly we don't want to have to explicitely define it

stv_pools : STV_POOLS 'default' statevectors ('custom' stv_pool+)? ;    // default pools are for enemies without defined pools
stv_pool : POOL_ID statevectors ('default_rewards' POOL_ID)?;     // id, pool of statevectors, id of default reward pool
statevectors : ('random' | 'ordered') '[' stv (LIST_SEPARATOR stv)* ']' ;
stv :  '[' complex_number (LIST_SEPARATOR complex_number)* ']';

reward_pools : REWARD_POOLS 'default' default_reward_pool ('custom' reward_pool+)? ;    // default pools are for enemies without defined pools
default_reward_pool : draw_strategy (POOL_ID | collectibles) ;      // the default pool can either be an ID or a list of collectibles
reward_pool : POOL_ID collectibles ;     // id, pool of collectibles
collectibles : '[' collectible (LIST_SEPARATOR collectible)* ']' ;

// TOKEN

// Characters implicitely used for special purposes:
// [ ]      for highlighting headlines and grouping lists
// < >      to mark the beginning and the end of the dungeon
// _        to mark the use of predefined template rooms or hallways, _0 is always the non-existing/empty one
// .        .. is used for an empty field in the map layout
// =        == is used for the non-existing hallway
// ~ | #    separators for Layout and Rooms for visual indications
// :        to mark the beginning of a room's content
// + -      signs for numbers
// ;        optical separation, e.g. can be use to separate things without a new line

// general token
DIGIT : [0-9] ;
NUMBER : DIGIT DIGIT DIGIT+ ;
IMAG_NUMBER : DIGIT* 'j' ;
SIGN : '-' | '+' ;
CHARACTER_LOW : [a-z] ;
CHARACTER_UP : [A-Z] ;
CHARACTER : CHARACTER_LOW | CHARACTER_UP ;

// headline token
HEADER : 'Qrogue<' ;
ENDER : '>Qrogue' ;
LAYOUT : '[Layout]' ;
ROOMS : '[Custom Rooms]' ;
HALLWAYS : '[Hallways]' ;
STV_POOLS : '[StateVector Pools]' ;
REWARD_POOLS : '[Reward Pools]' ;

// optical separators
HORIZONTAL_SEPARATOR : '~' ;
VERTICAL_SEPARATOR : '|' ;
LIST_SEPARATOR : ',' ;
WALL : '#' ;
EMPTY_FIELD : '..' ;

// keywords
DIRECTION : 'North' | 'East' | 'South' | 'West' ;
ORDERED_DRAW : 'ordered' ;
RANDOM_DRAW : 'random' ;

// ids
ROOM_ID : ('_' | CHARACTER) CHARACTER ;
HALLWAY_ID :'==' | ('_' | DIGIT) DIGIT ;   // '==' default (closed, no entanglement), same as _1 but with better visuals
POOL_ID : '*' (CHARACTER | DIGIT)+ ;

// ignored characters (whitespace and comments)
WS : [ \t\r\n]+ -> skip ;
UNIVERSAL_SEPARATOR : ';'+ -> skip ;
COMMENT : '/*' .*? '*/' -> skip ;
LINE_COMMENT : '//' ~[\r\n]* -> skip ;