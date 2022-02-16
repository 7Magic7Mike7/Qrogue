grammar QrogueWorld;

// RULES

start  : HEADER layout rooms hallways ENDER;

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
room : ROOM_ID r_attributes ':'
            'description' TEXT                // world/level description
            'teleport' REFERENCE ;  // which world/level to load
r_attributes : '(' r_visibility r_type DIRECTION ')' ;  // visibile/in sight, type, orientation of info text
r_visibility : (VISIBLE_LITERAL | FOGGY_LITERAL)? ;
r_type :  (WORLD_LITERAL | LEVEL_LITERAL) ;


// describing the hallways used in the layout (except for the default one '==')
hallways : HALLWAYS hallway*;
hallway : HALLWAY_ID h_attributes ;
h_attributes : '(' (OPEN_LITERAL | EVENT_LITERAL REFERENCE) ')' ;

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
CHARACTER_LOW : [a-z] ;
CHARACTER_UP : [A-Z] ;
CHARACTER : CHARACTER_LOW | CHARACTER_UP ;
TEXT : '"' .*? '"' ;

// literals
VISIBLE_LITERAL : 'visible' ;
FOGGY_LITERAL : 'foggy' ;

OPEN_LITERAL : 'open' ;
EVENT_LITERAL : 'event' ;

// headline token
HEADER : 'Qrogue<' ;
ENDER : '>Qrogue' ;
ROBOT : '[Robot]' ;
LAYOUT : '[Layout]' ;
ROOMS : '[Rooms]' ;
HALLWAYS : '[Hallways]' ;
MESSAGES : '[Messages]' ;

// optical separators
HORIZONTAL_SEPARATOR : '~' ;
VERTICAL_SEPARATOR : '|' ;
LIST_SEPARATOR : ',' ;
WALL : '#' ;
EMPTY_HALLWAY : '..' ;
EMPTY_ROOM : '__' ;

// keywords
WORLD_LITERAL : 'World' ;
LEVEL_LITERAL : 'Level' ;
DIRECTION : 'North' | 'East' | 'South' | 'West' ;

// ids
ROOM_ID : ('_' | CHARACTER) CHARACTER ;
HALLWAY_ID : '==' | ('_' | DIGIT) DIGIT ;   // '==' default (closed, no entanglement), same as _1 but with better visuals
REFERENCE : '*' (CHARACTER | DIGIT)+ ;

// ignored characters (whitespace and comments)
WS : [ \t\r\n]+ -> skip ;
UNIVERSAL_SEPARATOR : ';'+ -> skip ;
COMMENT : '/*' .*? '*/' -> skip ;
LINE_COMMENT : '//' ~[\r\n]* -> skip ;