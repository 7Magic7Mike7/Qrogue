from enum import Enum
from qrogue.util.config import ColorConfig as CC


class _HL:
    # objects
    boss = CC.highlight_object("Boss")
    circuit = CC.highlight_object("Circuit")
    coins = CC.highlight_object("Coins")
    collec = CC.highlight_object("Collectibles")
    door = CC.highlight_object("Door")
    enemies = CC.highlight_object("Enemies")
    gates = CC.highlight_object("Gates")
    key = CC.highlight_object("key")

    quantum_circuit = CC.highlight_object("Quantum Circuit")
    quantum_gates = CC.highlight_object("Quantum Gates")
    quantum_state = CC.highlight_object("Quantum State")
    qubits = CC.highlight_object("Qubits")
    qubit_s = CC.highlight_object("Qubit(s)")
    riddles = CC.highlight_object("Riddles")
    shop = CC.highlight_object("Shop")
    special_rooms = CC.highlight_object("Special Rooms")
    state = CC.highlight_object("State")
    state_vectors = CC.highlight_object("StateVectors")
    target_state = CC.highlight_object("Target State")

    # words
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
    help_ = CC.highlight_word("Help")
    hp = CC.highlight_word("don't lose HP")
    items = CC.highlight_word("Items")
    leave = CC.highlight_word("\"-Leave-\"")
    list_ = CC.highlight_word("list")
    locked = CC.highlight_word("locked")
    navigate = CC.highlight_word("navigate")
    not_zero = CC.highlight_word("not zero")
    one_hp = CC.highlight_word("1 HP")
    one_parenthesis = CC.highlight_word("1)")
    options = CC.highlight_word("Options")

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
    zeros = CC.highlight_word("zeros")

    # keys
    arrow_keys = CC.highlight_key("Arrow Keys")
    ctrl_q = CC.highlight_key("CTRL+Q")
    p = CC.highlight_key("P")
    q = CC.highlight_key("Q")
    space = CC.highlight_key("Space")

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

        HelpTextType.Controls:
            f"Move with the {_HL.arrow_keys}\n"
            f"Close Popups and select with {_HL.space}\n"
            f"Pause the game by pressing {_HL.p}\n\n"
            f"Should you ever get stuck you can force-quit the game by pressing {_HL.ctrl_q} and then {_HL.q}. This "
            "will still save the logs so it is the preferred option over simply closing the window!",

        HelpTextType.Fight:
            f"{_HL.one_parenthesis} In the middle of the screen you see 3 {_HL.state_vectors}. The left one (Current "
            f"State) corresponds to the output of your {_HL.circuit} (more on that later) while the right one "
            f"(Target State) is constant and depending on the "
            f"{_HL.enemy} you fight. You {_HL.win} the Fight by setting your Current State to the Target State by "
            f"adapting the mentioned Circuit. In between those two you can see their {_HL.difference}. If "
            f"it shows only {_HL.zeros} you reached your target and won the Fight!\n"
            f"{_HL.two_parenthesis} Underneath the StateVectors is your {_HL.circuit}. Currently you have 2 "
            f"{_HL.qubits} (q0, q1) and 0 out of 3 {_HL.gates} applied to them. The before mentioned Current "
            f"{_HL.state} reflects the output (out) of your {_HL.circuit}.\n"
            f"{_HL.three_parenthesis} On the bottom left you can choose the {_HL.action} you want to take: \n"
            f"{_HL.add_remove} - Change your {_HL.circuit} with the {_HL.gates} available to you (selection to the right). "
            f"After selecting a {_HL.gate} you are asked on which {_HL.qubit_s} you want to place it. If you select an "
            f"already used one it will be {_HL.removed} from your Circuit instead.\n"
            f"{_HL.commit} - Commit your changes and update your {_HL.circuit}. If Difference is {_HL.not_zero} you "
            f"lose {_HL.one_hp}.\n"
            f"{_HL.items} - Use one of your Items to make the Fight {_HL.easier} (you don't have any Items yet!)\n"
            f"{_HL.flee} - Try to flee from the Fight. This is {_HL.chance_based} and you lose {_HL.one_hp} if you "
            f"fail to flee (Note: for Tutorial purposes you {_HL.cannot_flee} in this Room!)\n"
            f"{_HL.four_parenthesis} The bottom right {_HL.display_details} based on the action you chose on the left "
            f"side. E.g. you can select the {_HL.gate} you want to use in your {_HL.circuit}.\n"
            f"{_HL.five_parenthesis} Use your {_HL.arrow_keys} to {_HL.navigate} between your available options at the "
            f"bottom and press {_HL.space} to {_HL.use} the selected one. Again, your goal now is to reach the "
            f"{_HL.target_state} of the {_HL.enemy}. If you succeed, you will get a {_HL.reward}!",

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
            f"{_HL.options} - Configure some Options of the game, like font size or coloring.\n"
            f"{_HL.help_} - If you ever feel stuck and don't remember how certain stuff in the game works select "
            f"this menu and we will try to help you.\n"
            f"{_HL.exit_} - Exit your current Playthrough and go back to the Main Menu.\n",

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
