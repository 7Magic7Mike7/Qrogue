grammar QrogueAreas;

import QrogueBasics;


// building the layout of a map
layout : LAYOUT HORIZONTAL_SEPARATOR* l_room_row (l_hallway_row l_room_row)* HORIZONTAL_SEPARATOR* ;
l_room_row :    VERTICAL_SEPARATOR
                (ROOM_ID | EMPTY_ROOM)  ((HALLWAY_ID | EMPTY_HALLWAY)   (ROOM_ID | EMPTY_ROOM))*
                VERTICAL_SEPARATOR ;
l_hallway_row : VERTICAL_SEPARATOR
                (HALLWAY_ID | EMPTY_HALLWAY)+
                VERTICAL_SEPARATOR ;

rooms : ROOMS room* ;
room : ROOM_ID r_attributes ':' room_content ;
r_attributes : '(' r_visibility r_type ')' ;  // visibile/in sight, type
r_visibility : (VISIBLE_LITERAL | FOGGY_LITERAL)? ;
r_type :    (SPAWN_LITERAL | BOSS_LITERAL | WILD_LITERAL | SHOP_LITERAL | RIDDLE_LITERAL | GATE_ROOM_LITERAL |
            TREASURE_LITERAL) ;
room_content : 'TODO: implement in importing grammar #override' ;    // must be implemented in importing grammar


// describing the hallways used in the layout (except for the default one '==')
hallways : HALLWAYS hallway*;
hallway : HALLWAY_ID h_attributes ;
h_attributes : '(' (OPEN_LITERAL | CLOSED_LITERAL | LOCKED_LITERAL | EVENT_LITERAL REFERENCE)
                ('one way' DIRECTION PERMANENT_LITERAL?)?
                ('entangled' '[' HALLWAY_ID (LIST_SEPARATOR HALLWAY_ID)* ']')? ')'  // (ENTANGLED_LITERAL)? ')'
                (TUTORIAL_LITERAL REFERENCE)?
                (TRIGGER_LITERAL REFERENCE)? ;

// headlines (encapsulated in '[' ']')
LAYOUT : '[Layout]' ;
ROOMS : '[Custom Rooms]' | '[Rooms]' ;
HALLWAYS : '[Hallways]' ;

// Area visibility
VISIBLE_LITERAL : 'visible' ;
FOGGY_LITERAL : 'foggy' ;

// Room Types
WORLD_LITERAL : 'World' ;
LEVEL_LITERAL : 'Level' ;

SPAWN_LITERAL : 'Spawn' ;
WILD_LITERAL : 'Wild' ;
SHOP_LITERAL : 'Shop' ;
RIDDLE_LITERAL : 'Riddle' ;
BOSS_LITERAL : 'Boss' ;
GATE_ROOM_LITERAL : 'Gate' ;
TREASURE_LITERAL : 'Treasure' ;

// door literals
OPEN_LITERAL : 'open' ;
CLOSED_LITERAL : 'closed' ;
LOCKED_LITERAL : 'locked' ;
EVENT_LITERAL : 'event' ;

PERMANENT_LITERAL: 'permanent' ;
ENTANGLED_LITERAL: 'entangled' ;
