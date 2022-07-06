grammar QrogueBasics;

// ###  RULES  ################################################################

// math
integer : DIGIT | HALLWAY_ID | INTEGER ;
complex_number : SIGN? (IMAG_NUMBER | (integer | FLOAT) (SIGN IMAG_NUMBER)?) ;

// ###  TOKEN  ################################################################

// keywords
DIRECTION : 'North' | 'East' | 'South' | 'West' ;

// Characters implicitely used for special purposes:
// < >      to mark the beginning and the end of the dungeon
// [ ]      for highlighting headlines and grouping lists
// _        single: Floor-tile | double: to mark the use of predefined template rooms or hallways
// .        double: is used for an empty field in the map layout, in combination with digits or characters as comma for floats or tile descriptor
// =        double: is used for the non-existing hallway
// ~ | #    separators for Layout and Rooms for visual indications
// :        to mark the beginning of a room's content
// + -      signs for numbers
// ;        optical separation, e.g. can be use to separate things without a new line
// *        marks the beginning of a pool id (inspired by pointers)

// literals
TUTORIAL_LITERAL : 'tutorial' ;
TRIGGER_LITERAL : 'trigger' ;

// headlines
HEADER : 'Qrogue<' ;
ENDER : '>Qrogue' ;

// separators
HORIZONTAL_SEPARATOR : '~' ;
VERTICAL_SEPARATOR : '|' ;
LIST_SEPARATOR : ',' ;
WALL : '#' ;
EMPTY_HALLWAY : '..' ;  // "empty" here means "non-existent"
EMPTY_ROOM : '__' ;     // "empty" here means "non-existent"

// mathematical token
DIGIT : [0-9] ;
INTEGER : DIGIT DIGIT DIGIT+ ;
FLOAT : DIGIT? '.' DIGIT+ ;
IMAG_NUMBER : (DIGIT* | FLOAT) 'j' ;
SIGN : '+' | '-' ;

// textual token
CHARACTER_LOW : [a-z] ;
CHARACTER_UP : [A-Z] ;
CHARACTER : CHARACTER_LOW | CHARACTER_UP ;
TEXT : '"' .*? '"' ;

// ids
ROOM_ID : ('_' | CHARACTER) CHARACTER ;
HALLWAY_ID : '==' | ('_' | DIGIT) DIGIT ;   // '==' default (closed, no entanglement), same as _1 but with better visuals
REFERENCE : '*' (CHARACTER | DIGIT)+ ;      // ids/references starting with "_" can be used for generated stuff without possible name collisions

// ignored characters (whitespace and comments)
WS : [ \t\r\n]+ -> skip ;
UNIVERSAL_SEPARATOR : ';'+ -> skip ;
COMMENT : '/*' .*? '*/' -> skip ;
LINE_COMMENT : '//' ~[\r\n]* -> skip ;
