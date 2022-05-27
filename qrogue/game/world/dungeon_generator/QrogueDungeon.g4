grammar QrogueDungeon;

import QrogueBasics, QrogueAreas, QrogueMessage;

// RULES

start  :    HEADER ('Name' '=' TEXT)?
            robot layout rooms hallways stv_pools reward_pools messages
            ENDER;

robot: ROBOT DIGIT 'qubits' '[' REFERENCE (LIST_SEPARATOR REFERENCE)* ']' ;

// building the non-template rooms used in the layout (note: template rooms are pre-defined rooms)
room_content : WALL* r_row+ WALL* tile_descriptor* ;
r_row : WALL tile+ WALL ;
tile :  'o' | 't' | 'm' | DIGIT | 'c' | 'e' | 'r' | '$' | '_' ;    // obstacle, trigger, message, enemy, collectible,
                                                                   // energy, riddle, shop, floor
// further describing the tiles used in the room
tile_descriptor : (trigger_descriptor | message_descriptor |
                  enemy_descriptor | collectible_descriptor | energy_descriptor | riddle_descriptor | shop_descriptor)
                  (TILE_MESSAGE_LITERAL REFERENCE)? (TILE_EVENT_LITERAL REFERENCE)? ;  // winning a fight or picking up a collectible can also trigger an event
trigger_descriptor : 't' REFERENCE ;   // reference to the event to trigger
message_descriptor : 'm' integer? REFERENCE ;    // #times displayed, reference to the text that should be shown
enemy_descriptor : DIGIT REFERENCE REFERENCE?;    // enemy, id of statevector pool, id of reward pool
collectible_descriptor : 'c' REFERENCE integer? ; // id of reward pool to draw from, number of rewards to draw (note: template pools like *key provide "normal" collectibles)
energy_descriptor : 'e' integer ;    // amount
riddle_descriptor : 'r' (REFERENCE | stv) (REFERENCE | collectible) integer;   // stv pool id, reward pool id, attempts
shop_descriptor : '$' (REFERENCE | collectibles) integer ;   // reward pool id or collectible list, num of items to draw


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
collectible :   (KEY_LITERAL integer | COIN_LITERAL integer | ENERGY_LITERAL integer | GATE_LITERAL REFERENCE |
                QUBIT_LITERAL integer?) ;

// TOKEN

// headlines (encapsulated in '[' ']')
ROBOT : '[Robot]' ;
STV_POOLS : '[StateVector Pools]' ;
REWARD_POOLS : '[Reward Pools]' ;

// Tile descriptor literals
TILE_MESSAGE_LITERAL : TUTORIAL_LITERAL ; //'tutorial' ;
TILE_EVENT_LITERAL : TRIGGER_LITERAL ; // 'trigger' ;

// tiles (token used for easier identification in generator)
KEY_LITERAL : 'key' ;
COIN_LITERAL : 'coin' ;
ENERGY_LITERAL : 'energy' ;
GATE_LITERAL : 'gate' ;
QUBIT_LITERAL : 'qubit' ;

// draw strategies (token used for easier identification in generator)
ORDERED_DRAW : 'ordered' ;
RANDOM_DRAW : 'random' ;
