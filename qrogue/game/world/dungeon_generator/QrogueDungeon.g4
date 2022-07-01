grammar QrogueDungeon;

import QrogueBasics, QrogueAreas, QrogueMessage;

// RULES

start  :    HEADER meta
            robot layout rooms hallways stv_pools reward_pools messages
            ENDER;

meta :  ('Name' '=' TEXT)?
        ('Description' '=' (message_body | REFERENCE))?
        (NO_TELEPORTER | WITH_TELEPORTER)? ;

robot : ROBOT DIGIT 'qubits' '[' REFERENCE (LIST_SEPARATOR REFERENCE)* ']'
        (CIRCUIT_SPACE '=' integer)? (BACKPACK_SPACE '=' integer)?
        (MAX_ENERGY '=' integer (START_ENERGY '=' integer)?)? ;

// building the non-template rooms used in the layout (note: template rooms are pre-defined rooms)
room_content : WALL* r_row+ WALL* tile_descriptor* ;
r_row : WALL tile+ WALL ;
tile :  'o' | 't' | 'm' | DIGIT | 'c' | 'e' | 'r' | '$' | '_' ;    // obstacle, trigger, message, enemy, collectible,
                                                                   // energy, riddle, shop, floor
// further describing the tiles used in the room
tile_descriptor : (t_descriptor | message_descriptor |
                  enemy_descriptor | collectible_descriptor | energy_descriptor | riddle_descriptor | shop_descriptor)
                  (TUTORIAL_LITERAL REFERENCE)? (TRIGGER_LITERAL REFERENCE)? ;  // winning a fight or picking up a collectible can also trigger an event
t_descriptor : 't' (trigger_descriptor | teleport_descriptor) ;
trigger_descriptor : (LEVEL_EVENT | GLOBAL_ACHIEVEMENT)? REFERENCE ;
teleport_descriptor : (LOCAL_TUNNEL ROOM_ID integer?) |     // no integer given equals middle of room
                      (GLOBAL_TELEPORT REFERENCE) ;
message_descriptor : 'm' integer? REFERENCE ;    // #times displayed, reference to the text that should be shown
enemy_descriptor : DIGIT (REFERENCE | stv) (REFERENCE | collectible)? ;    // enemy, id of statevector pool, id of reward pool
collectible_descriptor : 'c' ((REFERENCE integer?) | collectible) ; // id of reward pool to draw from, number of rewards to draw (note: template pools like *key provide "normal" collectibles)
energy_descriptor : 'e' integer ;    // amount
riddle_descriptor : 'r' integer (REFERENCE | stv) (REFERENCE | collectible) ;   // attempts, stv pool id, reward pool id
shop_descriptor : '$' integer (REFERENCE | collectibles) ;   // num of items to draw, reward pool id or collectible list


// how to draw an element from a pool
draw_strategy : RANDOM_DRAW | ORDERED_DRAW ;    // default is random draw, because mostly we don't want to have to explicitely define it

stv_pools : STV_POOLS ('custom' stv_pool+)? 'default' default_stv_pool ;    // default pools are for enemies without defined pools
default_stv_pool : REFERENCE | draw_strategy? stvs ;
stv_pool : REFERENCE draw_strategy? stvs ('default' 'rewards' ':' REFERENCE)?;     // id of pool, list of statevectors, id of default reward pool
stvs : '[' stv_ref (LIST_SEPARATOR stv_ref)* ']' ;
stv_ref: stv | REFERENCE ;
stv :  '[' complex_number (LIST_SEPARATOR complex_number)* ']';

reward_pools : REWARD_POOLS ('custom' reward_pool+)? 'default' default_reward_pool ;    // default pools are for enemies without defined pools
default_reward_pool : REFERENCE | draw_strategy? collectibles ;      // the default pool can either be an ID or a list of collectibles
reward_pool : REFERENCE draw_strategy? collectibles ;     // id, pool of collectibles
collectibles : '[' collectible (LIST_SEPARATOR collectible)* ']' ;
collectible :   (KEY_LITERAL integer | COIN_LITERAL integer | ENERGY_LITERAL integer | GATE_LITERAL REFERENCE |
                QUBIT_LITERAL integer?) ;

// TOKEN

// meta literals
SR_TELEPORTER : (('spawnroom' | 'SPAWNROOM' | 'sr' | 'SR' )'_'?)?  ('teleporter' | 'TELEPORTER') ;
NO_TELEPORTER : ('exclude' | 'EXCLUDE' | 'no' | 'NO') '_'? SR_TELEPORTER ;
WITH_TELEPORTER : ('include' | 'INCLUDE' | 'with' | 'WITH') '_'? SR_TELEPORTER ;

// headlines (encapsulated in '[' ']')
ROBOT : '[Robot]' ;
STV_POOLS : '[StateVector Pools]' ;
REWARD_POOLS : '[Reward Pools]' ;

// robot literals
MAX_ENERGY : ('max' | 'MAX') '_'? ('energy' | 'ENERGY') ;
START_ENERGY : ('start' | 'START') '_'? ('energy' | 'ENERGY') ;
CIRCUIT_SPACE : ('circuit' | 'CIRCUIT') '_'? ('space' | 'SPACE') ;
BACKPACK_SPACE : ('backpack' | 'BACKPACK') '_'? ('space' | 'SPACE') ;

// collectible tiles (token used for easier identification in generator)
KEY_LITERAL : 'key' ;
COIN_LITERAL : 'coin' ;
ENERGY_LITERAL : 'energy' ;
GATE_LITERAL : 'gate' ;
QUBIT_LITERAL : 'qubit' ;

// trigger tiles
LEVEL_EVENT : 'LevelEvent' ;
GLOBAL_ACHIEVEMENT : 'GlobalAchievement' ;

// teleport tiles
LOCAL_TUNNEL : 'tunnel' ;
GLOBAL_TELEPORT : 'teleport' ;

// draw strategies (token used for easier identification in generator)
ORDERED_DRAW : 'ordered' ;
RANDOM_DRAW : 'random' ;
