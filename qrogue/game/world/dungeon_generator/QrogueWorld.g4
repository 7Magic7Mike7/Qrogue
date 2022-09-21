grammar QrogueWorld;

import QrogueBasics, QrogueAreas, QrogueMessage;

// RULES

start  :    HEADER meta
            layout rooms hallways
            ENDER ;

meta :  ('Name' '=' TEXT)?
        ('Description' '=' message_body (MSG_EVENT REFERENCE MSG_ALTERNATIVE '*none')?)? ;

// building the non-template rooms used in the layout (note: template rooms are pre-defined rooms)
room_content :      OPTIONAL_LEVEL?
                    'description' message_body                // world/level description
                    'teleport' REFERENCE ;  // which world/level to load
r_type :  (WORLD_LITERAL | LEVEL_LITERAL) DIGIT DIGIT? DIRECTION ;

// TOKEN
OPTIONAL_LEVEL : 'optional' ;
