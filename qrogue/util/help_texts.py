from enum import Enum

from qrogue.util.config import ColorConfig as CC


class _HL:
    # objects
    boss = CC.highlight_object("Boss")
    circuit = CC.highlight_object("Circuit")
    coins = CC.highlight_object("Coins")
    collec = CC.highlight_object("Collectibles")
    current_state = CC.highlight_object("Current State")
    door = CC.highlight_object("Door")
    enemies = CC.highlight_object("Enemies")
    energy = CC.highlight_object("Energy")
    gates = CC.highlight_object("Gates")
    key = CC.highlight_object("Key")
    keys = CC.highlight_object("Keys")

    puzzle = CC.highlight_object("Puzzle")
    quantum_circuit = CC.highlight_object("Quantum Circuit")
    quantum_gates = CC.highlight_object("Quantum Gates")
    quantum_state = CC.highlight_object("Quantum State")
    qubit = CC.highlight_object("Qubit")
    qubits = CC.highlight_object("Qubits")
    qubit_s = CC.highlight_object("Qubit(s)")
    riddles = CC.highlight_object("Riddles")
    robot = CC.highlight_object("Robot")
    shop = CC.highlight_object("Shop")
    special_rooms = CC.highlight_object("Special Rooms")
    state = CC.highlight_object("State")
    state_vectors = CC.highlight_object("StateVectors")
    target_state = CC.highlight_object("Target State")

    # words
    abort = CC.highlight_word("abort")
    action = CC.highlight_word("action")
    add_remove = CC.highlight_word("Add/remove")
    attempt = CC.highlight_word("Attempt")
    bell = CC.highlight_word("Bell, the Master of Entanglement")
    both0 = CC.highlight_word("both 0")
    both1 = CC.highlight_word("both 1")
    buy = CC.highlight_word("buy")

    cannot_flee = CC.highlight_word("cannot flee")
    chance_based = CC.highlight_word("chance based")
    commit = CC.highlight_word("Commit")
    continue_ = CC.highlight_word("Continue")
    details = CC.highlight_word("details")
    difference = CC.highlight_word("Difference")
    display = CC.highlight_word("display")
    display_details = CC.highlight_word("displays details")
    easier = CC.highlight_word("easier")
    enemy = CC.highlight_object("Enemy")
    entanglement = CC.highlight_word("Entanglement")
    exit_ = CC.highlight_word("Exit")
    fights = CC.highlight_word("Fights")
    fight = CC.highlight_word("Fight")
    five_parenthesis = CC.highlight_word("5)")
    flee = CC.highlight_word("Flee")
    four_parenthesis = CC.highlight_word("4)")

    gate = CC.highlight_object("Gate")
    give_up = CC.highlight_word("\"Give up\"")
    help_ = CC.highlight_word("Manual")
    hp = CC.highlight_word("don't lose HP")
    items = CC.highlight_word("Items")
    leave = CC.highlight_word("\"-Leave-\"")
    level = CC.highlight_word("Level")
    list_ = CC.highlight_word("list")
    locked = CC.highlight_word("locked")
    loses_energy = CC.highlight_word("loses some Energy")
    map_ = CC.highlight_word("map")
    manual = CC.highlight_word("Manual")
    navigate = CC.highlight_word("navigate")
    not_zero = CC.highlight_word("not zero")
    one_hp = CC.highlight_word("1 HP")
    one_parenthesis = CC.highlight_word("1)")
    options = CC.highlight_word("Options")

    position = CC.highlight_word("Position")
    quantum_computing = CC.highlight_word("Quantum Computing")
    quantum_algorithm = CC.highlight_word("Quantum Algorithm")
    reenter = CC.highlight_word("re-enter")
    removed = CC.highlight_word("removed")
    reward = CC.highlight_word("Reward")
    serious = CC.highlight_word("serious")
    two_parenthesis = CC.highlight_word("2)")
    three_parenthesis = CC.highlight_word("3)")
    use = CC.highlight_word("use")
    vanishes = CC.highlight_word("vanishes")
    win = CC.highlight_word("win")
    zero_energy = CC.highlight_word("0 energy")
    zeros = CC.highlight_word("zeros")

    # keys
    arrow_keys = CC.highlight_key("Arrow Keys")
    backspace = CC.highlight_key("Backspace")
    ctrl_q = CC.highlight_key("CTRL+Q")
    h = CC.highlight_key("H")
    enter = CC.highlight_key("Enter")
    escape = CC.highlight_key("ESC")
    p = CC.highlight_key("P")
    q = CC.highlight_key("Q")
    shift_a = CC.highlight_key("Shift+A")
    shortcuts = CC.highlight_key("0") + ", " + CC.highlight_key("1") + ", ... , " + CC.highlight_key("9")
    space = CC.highlight_key("Space")
    tab = CC.highlight_key("TAB")
    wasd = CC.highlight_key("WASD")

    # tiles
    DOOR_TILE = CC.highlight_tile("-")
    TUTORIAL_TILE = CC.highlight_tile(".")


class HelpTextType(Enum):
    Controls = 0
    Fight = 1
    Riddle = 2
    Shop = 3
    BossFight = 4
    Game = 5
    Pause = 6
    Options = 7
    Welcome = 8
    FirstLevelIntroduction = 9


class HelpText:
    __DIC = {
        HelpTextType.Welcome:
            f"Qrogue is a game about {_HL.quantum_computing}. You will explore "
            f"Dungeons with the help of {_HL.quantum_gates} you can use for your "
            f"{_HL.quantum_circuit}. But you are not the only one in the Dungeons! "
            f"There are {_HL.enemies} challenging you to reach a certain "
            f"{_HL.quantum_state}. Your goal is to expand your library of "
            f"{_HL.quantum_gates} which are hidden in "
            f"{_HL.special_rooms} in the Dungeon or guarded "
            f"by a {_HL.boss} - a special Enemy that wants to see a "
            f"{_HL.quantum_algorithm} from you...\n"
            f"Now let's start! Try to move around with the {_HL.arrow_keys} and "
            f"go to the {_HL.door} ({_HL.DOOR_TILE}) at the bottom!"
            f"\nThe fields with a {_HL.TUTORIAL_TILE} will show you the next steps. "
            f"Now close this dialog and start playing by pressing {_HL.space}.",

        HelpTextType.FirstLevelIntroduction:
            f"Alright, let's have a look at the {_HL.display}.\n"
            f"The HUD is at the very top and shows you the current {_HL.level}, the {_HL.energy} of the "
            f"{_HL.robot} and the number of {_HL.coins} and {_HL.keys} it is carrying. Always keep an eye on your "
            f"current energy as {_HL.zero_energy} means we can no longer control the {_HL.robot} and have to "
            f"{_HL.abort} the {_HL.level}.\n"
            f"The rest of the screen shows a {_HL.map_} of the area our Robot's currently in. Next try to move the "
            f"Robot to the top left corner of the current room.",

        HelpTextType.Controls:
            f"That's the {_HL.manual}. You can always reopen it from the pause menu. Have a look at it and don't "
            f"forget to scroll down to see everything!\n"
            f"Move                  -   {_HL.arrow_keys}, {_HL.wasd}\n"
            f"Navigate menus        -   {_HL.arrow_keys}, {_HL.wasd}\n"
            f"Confirm               -   {_HL.enter}, {_HL.space}\n"
            f"Cancel/Back           -   {_HL.backspace}, {_HL.shift_a}\n"
            f"Scroll in message     -   {_HL.arrow_keys}, {_HL.wasd}\n"
            f"Close message         -   {_HL.enter}, {_HL.space}, {_HL.escape}\n"
            f"Reopen last message   -   {_HL.h}\n"
            f"Pause                 -   {_HL.p}, {_HL.tab}\n"
            f"Selection shortcuts   -   {_HL.shortcuts}\n"
            #"\n"
            f"[Should you ever get stuck you can force-quit the game by pressing {_HL.ctrl_q} and then {_HL.q}. This "
            "will still save the logs so it is the preferred option over simply closing the window!]",

        HelpTextType.Fight:
            f"{_HL.one_parenthesis} Below the HUD you can see three columns. The left one "
            f"(Current State) corresponds to the output of your {_HL.circuit} (more on that later) while the right one "
            f"(Target State) is constant and shows the Puzzle we want to solve. As soon as the current state matches "
            f"the target state the Puzzle will count as solved. The difference of the two states (i.e. what is still "
            f"missing to solve the Puzzle) is displayed in the middle one of the three columns. Therefore, if it only "
            f"shows {_HL.zeros} you win!\n"
        
            f"{_HL.two_parenthesis} Underneath the States (also called StateVectors due to their shape) is the "
            f"{_HL.circuit}. Currently we have 1 {_HL.qubit} q0 and 0 out of 3 {_HL.gates} applied to them. The "
            f"before mentioned {_HL.current_state} reflects the output (out) of the {_HL.circuit} and depends on the "
            f"{_HL.gates} we applied.\n"
            
            f"{_HL.three_parenthesis} On the bottom left you can choose the {_HL.action} you want to take: \n"
            f"{_HL.add_remove} - Change your {_HL.circuit} with the {_HL.gates} available to you (selection to the "
            f"right). After selecting a {_HL.gate} you have to define where to place it - so on which {_HL.qubit_s} "
            f"and on which {_HL.position}. If you select an already placed Gate you can either move it to a different "
            f"position or remove it from the Circuit.\n"
            f"{_HL.commit} - Commit your changes and update your Current State. If Difference is {_HL.not_zero} the "
            f"Robot {_HL.loses_energy}.\n"
            f"{_HL.items} - Use one of your Items to make the Puzzle {_HL.easier} (you don't have any Items yet!)\n"
            f"{_HL.flee} - Try to flee from the Fight. This is {_HL.chance_based} and you lose {_HL.one_hp} if you "
            f"fail to flee (Note: for Tutorial purposes you {_HL.cannot_flee} in this Room!)\n"
            
            f"{_HL.four_parenthesis} The bottom right {_HL.display_details} based on the action you chose on the left "
            f"side. E.g. you can select the {_HL.gate} you want to use in your {_HL.circuit}.\n"
            
            f"{_HL.five_parenthesis} Use your {_HL.arrow_keys} to {_HL.navigate} between your available options at the "
            f"bottom and press {_HL.space} to {_HL.use} the selected one. Again, your goal now is to reach the "
            f"{_HL.target_state} of the {_HL.puzzle}. If you succeed, you will get a {_HL.reward}!",

        HelpTextType.Riddle:
            f"{_HL.riddles} are very similar to {_HL.fights}. You have a {_HL.target_state} you need to reach (Difference is zero) "
            f"by adapting your {_HL.circuit}. The main difference is that you {_HL.hp} if you fail but instead 1 "
            f"{_HL.attempt} for solving the Riddle. When you have no more Attempts left the Riddle {_HL.vanishes} "
            "together with its reward - which is usually much better than the ones from Fights. Also fleeing (or in "
            f"this case {_HL.give_up}) will always work but obviously cost you your current {_HL.attempt} which is "
            f"why you are notified if this would lead to 0 Attempts left.",

        HelpTextType.Shop:
            f"In the {_HL.shop} you can use {_HL.coins} you got (e.g. from Fights) to buy various {_HL.collec}. On the "
            f"left side is a {_HL.list_} of everything you can {_HL.buy}. Navigate as usual with your {_HL.arrow_keys} "
            f"and select something with {_HL.space} to see more {_HL.details} on the right side. There you can also "
            f"buy it.\n"
            f"{_HL.leave} obviously makes you leave the {_HL.shop}. You can always {_HL.reenter} it later if you want!",

        HelpTextType.BossFight: # todo make more generic
            f"Now it's getting {_HL.serious}! You are fighting against {_HL.bell}. For the {_HL.state} you need to reach to "
            f"defeat Bell your two {_HL.qubits} will always have to be the same: either {_HL.both0} or {_HL.both1}.\n"
            f"This is called {_HL.entanglement}.\n\n"
            "Good luck!",

        HelpTextType.Game:
            f"Qrogue is a game about {_HL.quantum_computing}. You will explore "
            f"Dungeons with the help of {_HL.quantum_gates} you can use for your "
            f"{_HL.quantum_circuit}. But you are not the only one in the Dungeons! "
            f"There are {_HL.enemies} challenging you to reach a certain "
            f"{_HL.quantum_state}. Your goal is to expand your library of "
            f"{_HL.quantum_gates} which are hidden in "
            f"{_HL.special_rooms} in the Dungeon or guarded "
            f"by a {_HL.boss} - a special Enemy that wants to see a "
            f"{_HL.quantum_algorithm} from you.\n",

        HelpTextType.Pause:
            "In the Pause Menu you can do several things:\n"
            f"{_HL.continue_} - Leave the Pause Menu and continue where you stopped.\n"
            f"{_HL.help_} - If you ever feel stuck and don't remember how certain stuff in the game works select "
            f"this menu and we will try to help you.\n"
            f"{_HL.options} - Configure some Options of the game, like font size or coloring.\n"
            f"{_HL.exit_} - Exit the current Level or Expedition and return to the Spaceship.\n",

        HelpTextType.Options:
            "",

    }

    @staticmethod
    def get(type: HelpTextType) -> str:
        return HelpText.__DIC[type]

    @staticmethod
    def load(type: str) -> str:
        for key in HelpText.__DIC.keys():
            if key.name.lower() == type.lower():
                return HelpText.__DIC[key]
        return None


class TutorialTextType(Enum):
    LockedDoorNoKey = 0
    LockedDoorKey = 1


class TutorialText:
    __DIC = {
        TutorialTextType.LockedDoorNoKey:
            f"Hmm, the {_HL.door} is {_HL.locked}. Let's see if we can find a {_HL.key} somewhere.",
        TutorialTextType.LockedDoorKey:
            f"Oh the {_HL.door} is {_HL.locked}. Luckily we've already found a {_HL.key} to open it!",
    }

    @staticmethod
    def get(type: TutorialTextType) -> str:
        return TutorialText.__DIC[type]

    @staticmethod
    def load(type: str) -> str:
        for key in TutorialText.__DIC.keys():
            if key.name.lower() == type.lower():
                return TutorialText.__DIC[key]
        return None
