For upcoming v0.4

# Must haves #
- +template email, gather contacts, website text

# Should haves #
- implement remaining changes proposed via Feedback
- consider space in backpack when buying from shop
- place collectible on the ground if you cannot pack a reward in your backpack?
- access Backpack (Inventory)
- automatic font size adaption
  - [x] instead, try to start terminal maximized and print clear error message
  - research if it is feasible to make a web app out of Qrogue

# For v0.5 #
- Popup overhaul
  - +provide different positions like Top, Left, Right, Bot, Center, ...
  - tweak padding
  - +add default Speaker to grammar
  - +add page indication
  - +define in grammar whether the Popup is important enough to be reopened
  - +define intro message on level start? might make event stuff a lot easier
  - +Confirmation popup with custom choices and arrow controls?
  - +if alternative message is *None or *null etc. no message is shown if event is satisfied
- Automated testing
- Documentation

# Tweaks #
- key input pauses?

# Optionals #
- use TextBox instead of BlockLabels?


# Ideas #
+ Wave Function Collapse algorithm to create random maps instead of the current approach
- when defeated by a puzzle, give option to continue trying in the trainings environment
- Expeditions with hard difficulty are not generated room-wise but dynamically based on WFC (would need tunneling though)
- fleeing pushes you back to your previous position? Else you could continue without having to solve a Puzzle, so special rewards could only be given as direct reward (bad for visuals since you don't see that)
  - would make it possible to unlock from the beginning (though we have to take care of events)
- overhaul puzzle UI:
  - add "Move" choice
  - only list unplaced gates (gets rid of positional details which are not needed if "Move" is an option)
  - "Remove" is used until player cancels (back) or circuit is empty (gets rid of "Reset")
  - maybe also add "Place" ("Edit" would be to general since move and remove also edit) option? 
  - this way the old "Confirm" can be done implicitely by going back after you're finished with placing/moving/removing and we don't have to implicitely commit on every change
  - don't tell the player all the time that the puzzle is not yet solved (they can see it cause the output is still red)

# Finished #
- raise Errors in Logger instead of arbitrary positions, so we can actually log them!
- implement normal Game Mode (playing without Tutorial Stuff on generated (?) Map)
  - [x] make chance parameter of WildRooms more stable so 0.7 means 70% of 
  all Tiles in the Room are Enemies
  - [x] further enhance Factories for random selection of Collectibles, Riddles, Bosses 
- start in debug mode (HUD logs, all error output, cheats, simulator)
- GameSimulator: seeds need to be set correctly so random stuff like flee chance doesn't hinder execution
- new Hub area
- new Tutorial based on Narrative update
- create Rooms from file
- custom GameData location also for Unix (via console arguments)
- PyPI upload:
https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56
- add Training-Table to Spaceship (implement with flee rate)
- Quickstart menu point to directly start where "Q" in the spaceship starts
- split tutorial into multiple small levels (w0 = exam on earth)
- show qubits in circuit and stv
- adapt "damaging" messages
- show attempts for Riddle in HUD
- Constraint based Puzzles (= "Challenges")
- implement multi moves (e.g. 6+W = move up 6 times)
