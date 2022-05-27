grammar QrogueMessage;

import QrogueBasics;

messages : MESSAGES message* ;
message : REFERENCE (MSG_SPEAKER TEXT)? TEXT+ (MSG_EVENT REFERENCE MSG_ALTERNATIVE REFERENCE)? ;    // alternative message if a certain event already happened

MESSAGES : '[Messages]' ;   // headline needs to be encapsulated in '[' ']'
MSG_EVENT : 'when' ;    // can't use 'if' because it consists of two characters which is reserved for ROOM_IDs
MSG_ALTERNATIVE : 'alternative' | 'then' ;
MSG_SPEAKER : 'speaker' | 'Speaker' ;
