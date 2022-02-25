# Playtesting Feedback of Qrogue v0.1



### Installation

Feedback | Underlying Issue | Priority | Proposed Solution | Done
| - | - | - | - | :-: |
macOS Support | no support yet | Medium | PR from Lukas |
execute "install.sh" from "installer" folder | not mentioned in Readme | High | PR from Lukas | 
PyPI package | downloading and installing in several steps is tedious | High | provide PyPI package | 


### Programmstart

Feedback | Underlying Issue | Priority | Proposed Solution | Done
| - | - | - | - | :-: |
terminal size error is frustrating | terminal needs a certain size for the game to work/render | High | print error description and fix directly in terminal | `x`
space to confirm in menu is not obvious | stated nowhere | High | add "Enter" to select controls and state controls in Readme | `x`
exception on instant exit | try to flush uninitialized KeyLogger | - | KeyLogger generated at beginning of playing | `x` 



### Gameplay

Feedback | Underlying Issue | Priority | Proposed Solution | Done
| - | - | - | - | :-: |
1/sqrt(2) = 0.71 looks weird | displaying 2 digits after comma | Low | use 3 digits | `x`
confusing that Difference is in the middle of the screen | | High | redesign of StateVector visualization | `x`
redundant repetition of truth table | truth table on the very left and very right | Medium | redesign of StateVector visualizatin | `x`
qubit order is inverse to convention | - | High | redesing of StateVector visualization | `x`
health display is confusing | border box renders - in front of value | High | try to find out why that's the case | 
tedious to navigate in fight menu | no shortcuts but much back and forth | High | add shortcuts to the actions | `x`
how to end the game? | no explanation how to access the pause menu | High | mention pause button | `x`
why is 10 hp the maximum? | no explanation why you cannot heal over 10 hp | High | display max hp (e.g. 7 / 10 HP) | `x`
I don't get the purpose of the different numbers | not described well enough | Medium | come up with a better description and smaller example | 
concept of entangled doors is wrong | not described well enough? | Low | come up with a better description? | 
misclick on gate selection tedious to undo | selection process cannot be canceled | Medium | key for cancel | `x`
insert position of gate not selectable | simple queue because of the original concept | High | keys for position | 

### Bugs
Feedback | Underlying Issue | Priority | Proposed Solution | Done
| - | - | - | - | :-: |
inconsitent visualization of amplitudes | hard coded in Tutorial | Low | Tutorial will be revamped anyways | 
"east" instead of "west" in Tutorial | forgot to adapt | Low | Tutorial will be revamped anyways | 
H(0) + Z(0) gives wrong StateVector | forgot to change underlying gate when I copied the code from XGate | High | change underlying gate to ZGate | `x`
