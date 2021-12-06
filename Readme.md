>           _______           
>          / _____ \          
>         | |     | |         
>         | |     | |         
>         | |     | |   _ __ ___   __ _ _   _  ___         
>         | |     | |  | '__/ _ \ / _` | | | |/ _ \
>         | |_____| |  | | | (_) | (_| | |_| |  __/    
>          \______\_\  |_|  \___/ \__, |\__,_|\___|   
>                                  __/ |            
>                                 |___/ 
ASCII-Art generated by https://www.ascii-art-generator.org/

# Qrogue v0.0.1 #

Qrogue is a Quantum Computing take of the classical game 
[Rogue](https://en.wikipedia.org/wiki/Rogue_%28video_game%29). 
You will navigate through randomly generated Dungeons to find 
Quantum Gates. During your search you will inevitably encounter 
Enemies you can only defeat by reaching a certain Quantum State - 
to do that you will need to use the Gates you collected!

## Installation ##


### Dependencies ###
- py_cui v0.1.4
- qiskit v0.32.0

However, both of these dependencies are installed automatically
in the virtual environment by the corresponding installer.

### Linux ###

#### Prerequisites ####

- Python 3.8
- python3-venv

For Linux you simply have to run `installer/install.sh` in your
downloaded Qrogue folder to create a new virtual environment for 
the game and install the required packages in there. 

Afterwards just run `play_qrogue.sh` to play the game.

### Windows ###

#### Prerequisites ####

- [Python 3.8](https://www.python.org/downloads/release/python-3812/)
- [Anaconda](https://anaconda.org/anaconda/python)

For Windows there is currently no script available that 
automatically installs everything you need. The best way is to 
create a new virtual environment with Anaconda Navigator (Python 3.8). 
Then open a terminal (e.g. Windows Powershell) and execute 
`installer\install.ps1`. You will be asked to provide the name of your 
newly created environment as well as the location you want to store your 
game data (e.g. save files, config) as parameter. 
This will install the required Packages in the virtual 
environment and setup a QrogueData folder in the specified location.

It is recommended to play the game in 
[Windows Terminal](https://www.microsoft.com/store/productId/9N0DX20HK701) 
for the best experience (a corresponding profile will be provided 
in the future!). However, every other console should also be fine. 
Simply execute `play_qrogue.ps1`

## Notes ##

- `py_cui.errors.PyCUIOutOfBoundsError` 

Should you ever encounter this error
when starting the game please try to maximize the console you 
use for playing. This is because currently there is no automatic 
font size adaption so depending on your console settings a 
minimum width and height is required. Alternatively or if 
maximizing doesn't help you can lower the font size of the 
console.

- newer Python versions

Usually also Python 3.9 and onward should perfectly work for 
playing Qrogue but testing is currently done for Python 3.8 so 
there is no official support yet for other versions. The same 
is true if you decide to manually install the dependencies; newer 
version will likely work but are not recommended.

## Outlook ##

What you can expect from Qrogue v0.1:

- Real game mode: Aside from the current Tutorial which acts 
as a proof of concept the normal game mode will take place in 
a randomly generated Dungeon with a random Boss, random available 
Gates etc.
- Bigger selection of Quantum Gates
- New Pickups
- Options Menu