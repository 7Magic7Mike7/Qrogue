grammar QrogueDungeon;

import QrogueBasics, QrogueAreas, QrogueMessage;

// RULES

start  :    HEADER meta
            robot layout rooms hallways stv_pools reward_pools messages
            ENDER;

meta :  ('Name' '=' TEXT)?
        ('Description' '=' (message_body | REFERENCE))?
        (NO_TELEPORTER | WITH_TELEPORTER)?
        SHOW_INDIV_QUBITS? ;

robot : ROBOT DIGIT 'qubits' '[' REFERENCE (LIST_SEPARATOR REFERENCE)* ']'
        (CIRCUIT_SPACE '=' integer)? (BACKPACK_SPACE '=' integer)?
        (MAX_ENERGY '=' integer (START_ENERGY '=' integer)?)? ;

// building the non-template rooms used in the layout (note: template rooms are pre-defined rooms)
room_content : WALL* r_row+ WALL* tile_descriptor* ;
r_row : WALL tile+ WALL ;
tile :  'o' | 't' | 'm' | DIGIT | 'b' | 'c' | 'e' | 'r' | '!' | '_' ;          // obstacle, trigger, message, enemy,
                                                                               // boss, collectible, energy, riddle,
                                                                               // challenge, floor
// further describing the tiles used in the room
tile_descriptor : (t_descriptor | message_descriptor |
                  enemy_descriptor | boss_descriptor | collectible_descriptor | energy_descriptor | riddle_descriptor |
                  challenge_descriptor)
                  (TUTORIAL_LITERAL REFERENCE)? (TRIGGER_LITERAL (REFERENCE | GLOBAL_EVENT_REFERENCE | UNLOCK_REFERENCE))? ;  // winning a fight or picking up a collectible can also trigger an event
t_descriptor : 't' (trigger_descriptor | teleport_descriptor) ;
trigger_descriptor : (LEVEL_EVENT | GLOBAL_ACHIEVEMENT | UNLOCK)? REFERENCE ;
teleport_descriptor : (LOCAL_TUNNEL ROOM_ID integer?) |     // no integer given equals middle of room
                      (GLOBAL_TELEPORT REFERENCE) ;
message_descriptor : 'm' integer? (REFERENCE | TEXT) ;    // #times displayed, reference to the text that should be shown
collectible_descriptor : 'c' ((REFERENCE integer?) | collectible) ; // id of reward pool to draw from, number of rewards to draw (note: template pools like *key provide "normal" collectibles)
energy_descriptor : 'e' integer ;    // amount

enemy_descriptor : DIGIT (REFERENCE | stv) (REFERENCE | collectible)? input_stv? ;    // enemy, target stv (pool id or explicit), reward (pool id or explicit)
boss_descriptor : 'b' REFERENCE (GATE_LITERAL REFERENCE)? (REFERENCE | collectible) integer ;   // boss reference, optional gate that should be part of the puzzle, collectible
riddle_descriptor : 'r' integer puzzle_parameter ;   // attempts
challenge_descriptor : '!' integer integer? puzzle_parameter ;  // min number of gates, max number of gates
puzzle_parameter : (REFERENCE | stv) (REFERENCE | collectible) input_stv? ;    // stv pool id, reward pool id
input_stv : ('input' | 'i') '=' (REFERENCE | stv) ;      // input statevector (pool id or explicit)
boss_puzzle : (REFERENCE | stv) input_stv ;

circuit_stv: NUM_QUBITS_SPECIFIER '=' DIGIT ':' (circuit_gate_single | circuit_gate_multi)
             (',' (circuit_gate_single | circuit_gate_multi))* ;
circuit_gate_single: (GATE_SPECIFIER | '[' GATE_SPECIFIER (',' GATE_SPECIFIER)* ']') '@' QUBIT_SPECIFIER ;
circuit_gate_multi: GATE_SPECIFIER '@' '[' QUBIT_SPECIFIER ',' QUBIT_SPECIFIER+ ']' ;   // gCX @ [q0, q1]

// how to draw an element from a pool
draw_strategy : RANDOM_DRAW | ORDERED_DRAW ;    // default is random draw, because mostly we don't want to have to explicitely define it

stv_pools : STV_POOLS ('custom' stv_pool+)? 'default' default_stv_pool ;    // default pools are for enemies without defined pools
default_stv_pool : REFERENCE | draw_strategy? stvs ;
stv_pool : REFERENCE draw_strategy? stvs ('default' 'rewards' ':' REFERENCE)?;     // id of pool, list of statevectors, id of default reward pool
stvs : '[' stv_ref (LIST_SEPARATOR stv_ref)* ']' ;
stv_ref: stv | REFERENCE ;
stv :  ('[' complex_number (LIST_SEPARATOR complex_number)* ']') | ('{' circuit_stv '}');

reward_pools : REWARD_POOLS ('custom' reward_pool+)? 'default' default_reward_pool ;    // default pools are for enemies without defined pools
default_reward_pool : REFERENCE | draw_strategy? collectibles ;      // the default pool can either be an ID or a list of collectibles
reward_pool : REFERENCE draw_strategy? collectibles ;     // id, pool of collectibles
collectibles : '[' collectible (LIST_SEPARATOR collectible)* ']' ;
collectible :   ((SCORE_LITERAL | KEY_LITERAL | ENERGY_LITERAL) integer |
                GATE_LITERAL REFERENCE | QUBIT_LITERAL integer? |
                NONE_LITERAL) ;

// TOKEN

// meta literals
SR_TELEPORTER : (('spawnroom' | 'SPAWNROOM' | 'sr' | 'SR' )'_'?)?  ('teleporter' | 'TELEPORTER') ;
NO_TELEPORTER : ('exclude' | 'EXCLUDE' | 'no' | 'NO') '_'? SR_TELEPORTER ;
WITH_TELEPORTER : ('include' | 'INCLUDE' | 'with' | 'WITH') '_'? SR_TELEPORTER ;
SHOW_INDIV_QUBITS : ('show' | 'SHOW') '_'? ('individual' | 'indiv' | 'INDIVIDUAL' | 'INDIV') '_'? ('qubits' | 'QUBITS') ;

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
SCORE_LITERAL : 'score' ;
KEY_LITERAL : 'key' ;
ENERGY_LITERAL : 'energy' ;
GATE_LITERAL : 'gate' ;
QUBIT_LITERAL : 'qubit' ;
NONE_LITERAL : 'none' ;

// trigger tiles
LEVEL_EVENT : 'LevelEvent' ;
GLOBAL_ACHIEVEMENT : 'GlobalAchievement' ;
UNLOCK : 'Unlocked' ;
GLOBAL_EVENT_REFERENCE : '*' 'global_event_' (CHARACTER | DIGIT)+ ;  // same as reference but with 'globalEvent_' prefix
UNLOCK_REFERENCE : '*' 'unlock_'  (CHARACTER | DIGIT)+ ;  // same as reference but with 'unlock_' prefix

// teleport tiles
LOCAL_TUNNEL : 'tunnel' ;
GLOBAL_TELEPORT : 'teleport' ;

// draw strategies (token used for easier identification in generator)
ORDERED_DRAW : 'ordered' ;
RANDOM_DRAW : 'random' ;

// statevector literals
NUM_QUBITS_SPECIFIER: 'num' '_'? 'qubits' ;
QUBIT_SPECIFIER: 'q' DIGIT ;
GATE_SPECIFIER: 'g' CHARACTER_UP CHARACTER* ;
