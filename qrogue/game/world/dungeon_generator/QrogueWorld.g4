grammar QrogueWorld;

import QrogueBasics, QrogueAreas, QrogueMessage;

// RULES

start  :    HEADER ('Name' '=' TEXT)?
            layout rooms hallways
            ENDER;

// building the non-template rooms used in the layout (note: template rooms are pre-defined rooms)
room_content :      'description' message_body                // world/level description
                    'teleport' REFERENCE ;  // which world/level to load
r_type :  (WORLD_LITERAL | LEVEL_LITERAL) DIGIT DIGIT? DIRECTION ;

// TOKEN
