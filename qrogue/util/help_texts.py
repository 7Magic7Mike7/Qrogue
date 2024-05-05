from enum import Enum
from typing import Optional, List

from qrogue.util.config import ColorConfig as CC


class _HL:
    # objects
    boss = CC.highlight_object("Boss")
    circuit = CC.highlight_object("Circuit")
    circuit_matrix = CC.highlight_object("Circuit Matrix")
    collec = CC.highlight_object("Collectibles")
    current_state = CC.highlight_object("Current State")
    door = CC.highlight_object("Door")
    enemies = CC.highlight_object("Enemies")
    energy = CC.highlight_object("Energy")
    gates = CC.highlight_object("Gates")
    gate_i = CC.highlight_object("I Gate")
    gate_cx = CC.highlight_object("CX Gate")
    gate_x = CC.highlight_object("X Gate")
    input_stv = CC.highlight_object("Input State Vector")
    ket_notation = CC.highlight_object("Ket-Notation")
    key = CC.highlight_object("Key")
    keys = CC.highlight_object("Keys")

    output_stv = CC.highlight_object("Output State Vector")
    puzzle = CC.highlight_object("Puzzle")
    puzzles = CC.highlight_object("Puzzles")
    quantum_circuit = CC.highlight_object("Quantum Circuit")
    quantum_gates = CC.highlight_object("Quantum Gates")
    quantum_state = CC.highlight_object("Quantum State")
    qubit = CC.highlight_object("Qubit")
    qubits = CC.highlight_object("Qubits")
    qubit_s = CC.highlight_object("Qubit(s)")
    riddles = CC.highlight_object("Riddles")
    robot = CC.highlight_object("Robot")
    special_rooms = CC.highlight_object("Special Rooms")
    state = CC.highlight_object("State")
    #state_vectors = CC.highlight_object("StateVectors")
    target_state = CC.highlight_object("Target State")
    target_stv = CC.highlight_object("Target State Vector")

    # actions
    applying = CC.highlight_action("applying")
    buy = CC.highlight_action("buy")
    change = CC.highlight_action("change")
    choose = CC.highlight_action("choose")
    editing = CC.highlight_action("editing")
    edit = CC.highlight_action("edit")
    edits = CC.highlight_action("edits")
    position = CC.highlight_action("position")
    place = CC.highlight_action("place")
    reach = CC.highlight_action("reach")
    select = CC.highlight_action("select")
    talk = CC.highlight_action("talk")
    try_ = CC.highlight_action("try")

    # words
    amplitude = CC.highlight_word("amplitude")
    amplitude_1 = CC.highlight_word("amplitude of 1")
    arbitrary = CC.highlight_word("arbitrary")
    around = CC.highlight_word("around")
    attempt = CC.highlight_word("Attempt")
    bell = CC.highlight_word("Bell, the Master of Entanglement")
    both0 = CC.highlight_word("both 0")
    both1 = CC.highlight_word("both 1")

    cannot = CC.highlight_word("cannot")
    chance_based = CC.highlight_word("chance based")
    collapses = CC.highlight_word("collapses")
    continue_ = CC.highlight_word("Continue")
    details = CC.highlight_word("details")
    deterministic = CC.highlight_word("deterministic")
    difference = CC.highlight_word("Difference")
    display_details = CC.highlight_word("displays details")
    easier = CC.highlight_word("easier")
    edit_attempts = CC.highlight_word("edit attempts")
    enemy = CC.highlight_object("Enemy")
    entanglement = CC.highlight_word("Entanglement")
    equal = CC.highlight_word("equal")
    exam = CC.highlight_word("Exam")
    exit_ = CC.highlight_word("Exit")
    expedition = CC.highlight_word("Expedition")
    finally_ = CC.highlight_word("finally")
    five_parenthesis = CC.highlight_word("5)")
    flee = CC.highlight_word("Flee")
    four = CC.highlight_word("four")
    four_parenthesis = CC.highlight_word("4)")

    gate = CC.highlight_object("Gate")
    give_up = CC.highlight_word("\"Give up\"")
    help_ = CC.highlight_word("Manual")
    hp = CC.highlight_word("don't lose Energy")
    items = CC.highlight_word("Items")
    ket1_symbol = CC.highlight_word("|?>")
    ket2_symbol = CC.highlight_word("|??>")
    ket_symbol_stv01 = CC.highlight_word("|0> 1")
    kronecker = CC.highlight_word("kronecker product")
    leave = CC.highlight_word("\"-Leave-\"")
    list_ = CC.highlight_word("list")
    location = CC.highlight_word("Location")
    locked = CC.highlight_word("locked")
    loses_energy = CC.highlight_word("loses some Energy")
    map_ = CC.highlight_word("map")
    manual = CC.highlight_word("Manual")
    matrix_2x2 = CC.highlight_word("2x2 matrix")
    matrix_4x4 = CC.highlight_word("4x4 matrix")
    mat_vec_mul = CC.highlight_word("matrix-vector multiplication")
    mission = CC.highlight_word("Mission")
    moon = CC.highlight_word("Moon")
    moon_mission = CC.highlight_word("Moon Mission")
    navigate = CC.highlight_word("navigate")
    navigation_panel = CC.highlight_word("Navigation Panel")
    not_zero = CC.highlight_word("not zero")
    number_of_times = CC.highlight_word("number of times")
    often = CC.highlight_word("often")
    one_hp = CC.highlight_word("1 HP")
    one_parenthesis = CC.highlight_word("1)")
    options = CC.highlight_word("Options")
    order = CC.highlight_word("order")
    probability = CC.highlight_word("probability")

    quantum_computing = CC.highlight_word("Quantum Computing")
    quantum_algorithm = CC.highlight_word("Quantum Algorithm")
    qubit_configuration = CC.highlight_word("qubit configuration")
    qubit_configurations = CC.highlight_word("qubit configurations")
    reenter = CC.highlight_word("re-enter")
    removed = CC.highlight_word("removed")
    restart = CC.highlight_word("Restart")
    reward = CC.highlight_word("Reward")
    save = CC.highlight_word("Save")
    serious = CC.highlight_word("serious")
    start_journey = CC.highlight_word("START YOUR JOURNEY")
    state_vector = CC.highlight_word("StateVector")
    state_vectors = CC.highlight_word("StateVectors")
    superposition = CC.highlight_word("Superposition")
    three_parenthesis = CC.highlight_word("3)")
    transforms = CC.highlight_word("transforms")
    two = CC.highlight_word("two")
    two_parenthesis = CC.highlight_word("2)")
    unstable = CC.highlight_word("unstable")
    use = CC.highlight_word("use")
    vanishes = CC.highlight_word("vanishes")
    vanish = CC.highlight_word("vanish")
    win = CC.highlight_word("win")
    zero_energy = CC.highlight_word("0 energy")
    zeros = CC.highlight_word("zeros")
    zero_state = CC.highlight_word("zero-state")

    # keys
    action_keys = CC.highlight_key("Space") + " or " + CC.highlight_key("Enter")
    cancel_keys = CC.highlight_key("Backspace") + " or " + CC.highlight_key("Shift+A") + " or " + \
        CC.highlight_key("Shift+Left")
    help_keys = CC.highlight_key("H")
    navigation_keys = CC.highlight_key("WASD") + " or " + CC.highlight_key("Arrow Keys")
    pause_keys = CC.highlight_key("P") + " or " + CC.highlight_key("TAB")
    shortcuts = CC.highlight_key("0") + ", " + CC.highlight_key("1") + ", ... , " + CC.highlight_key("9")
    shutdown_keys = CC.highlight_key("CTRL+Q") + " followed by " + CC.highlight_key("Q")

    # tiles
    door_tile = CC.highlight_tile("-")
    level_decoration_tile = CC.highlight_tile("L")
    level2_decoration_tile = CC.highlight_tile("L - 2")
    msg_tile = CC.highlight_tile(".")
    navigation_tile = CC.highlight_tile("N")
    quickstart_tile = CC.highlight_tile("Q")
    robb_tile = CC.highlight_tile("R")
    teleport_tile = CC.highlight_tile("t")


class HelpText(Enum):       # todo: import Controls to replace static key-mentions with dynamic ones?
    Controls = f"Move                  -   {_HL.navigation_keys}\n" \
            f"Navigate menus        -   {_HL.navigation_keys}\n" \
            f"Confirm               -   {_HL.action_keys}\n" \
            f"Cancel/Back           -   {_HL.cancel_keys}\n" \
            f"Scroll in message     -   {_HL.navigation_keys}\n" \
            f"Close message         -   {_HL.action_keys}\n" \
            f"Reopen last message   -   {_HL.help_keys}\n" \
            f"Pause                 -   {_HL.pause_keys}\n" \
            f"Selection shortcuts   -   {_HL.shortcuts}\n" \
            "\n" \
            f"[Should you ever get stuck try to open the pause menu with {_HL.pause_keys} and then select continue. " \
            f"This way the game refocuses and renders again. In case this still doesn't help or doesn't even work you "\
            f"can force-quit the game by pressing {_HL.shutdown_keys}. This will still save everything so it is the " \
            "preferred option over simply closing the window!]"  # let's not mention ESC since it could lead to bugs

    Fight = \
        f"Basically {_HL.quantum_computing} is just a lot of complex-valued {_HL.mat_vec_mul}:\n" \
        f"{_HL.circuit_matrix} * {_HL.input_stv} = {_HL.output_stv}\n" \
        f"Your goal is to make the latter {_HL.equal} to the {_HL.target_stv}. While the input and target state " \
        f"vector are given by the {_HL.puzzle}, you can {_HL.change} the {_HL.circuit_matrix} by {_HL.editing} your " \
        f"{_HL.circuit}.\n" \
        f"First you have to {_HL.select} a {_HL.gate} and then {_HL.place} it via {_HL.navigation_keys}. " \
        f"Afterwards use {_HL.action_keys} to confirm the placement. This will update both {_HL.circuit_matrix} " \
        f"and {_HL.output_stv} accordingly. Green numbers in {_HL.output_stv} indicate correct and red incorrect " \
        f"values. Once the whole vector is green, {_HL.output_stv} and {_HL.target_stv} are equal and the " \
        f"{_HL.puzzle} is solved."

    Ket = \
        f"The {_HL.ket1_symbol}-notation you can see {_HL.around} the {_HL.state_vectors} and {_HL.circuit_matrix} " \
        f"is called {_HL.ket_notation}. It describes to which {_HL.qubit_configuration} the values correspond to. For " \
        f"example {_HL.ket_symbol_stv01} at ~Target~ means that the target qubit's {_HL.zero_state} should have an " \
        f"{_HL.amplitude_1}, where the amplitude corresponds to a {_HL.probability} of how likely the described " \
        f"{_HL.state} occurs. Let's consider the following (transposed) {_HL.state_vector}:\n" \
        f"|00>  0.707\n" \
        f"|01>  0.707\n" \
        f"|10>    0  \n" \
        f"|11>    0  \n" \
        f"It implies that both {_HL.qubit_configurations} |00> and |01> have an amplitude of 0.707 and therefore " \
        f"correspond to a probability of abs(0.707)^2 = 0.5 = 50%. Since we write the most significant qubit first, " \
        f"this implies that q1=0 is always true and only q0's value comes down to a coin flip.\n" \
        f"In general {_HL.ket_notation} looks like this: |qn...q1q0>, where n is the number of qubits - 1."

    ParallelGates = \
        f"Single qubit {_HL.gates} (e.g., X Gate) correspond to {_HL.matrix_2x2} which describe how the {_HL.gate} " \
        f"{_HL.transforms} the two possible inputs (0 and 1). However, {_HL.circuit} with {_HL.two} {_HL.qubits} " \
        f"have {_HL.four} possible inputs (00, 01, 10 and 11) and therefore have to correspond to {_HL.matrix_4x4}. " \
        f"Hence, to extend the original 2x2 matrix of the X Gate we need to calculate a so-called {_HL.kronecker}.\n" \
        f"\n" \
        f"Let's consider a circuit with an {_HL.gate_x} applied to q0. What happens to q1?\n" \
        f"Not performing an operation on it is the same as {_HL.applying} the identity or {_HL.gate_i} (transforming " \
        f"0 to 0 and 1 to 1) to it. Now to calculate the {_HL.kronecker} of X (on q0) and I (on q1) we have to " \
        f"{CC.highlight_word('put X into I')} like this:\n" \
        "    |0>  |1>        |0> |1>\n" \
        "|0> 1*X  0*X  =  |0> X   0 \n" \
        "|1> 0*X  1*X     |1> 0   X \n" \
        "\n" \
        f"and furthermore as we {CC.highlight_word('unpack')} X:\n" \
        "    |00> |01> |10> |11>\n" \
        "|00>  0    1    0    0 \n" \
        "|01>  1    0    0    0 \n" \
        "|10>  0    0    0    1 \n" \
        "|11>  0    0    1    0 \n" \
        "\n" \
        f"The order is important as {CC.highlight_word('putting X into I')} results in a different matrix than " \
        f"{CC.highlight_word('putting I into X')}. But if you look at your {_HL.circuit} you can always go from " \
        f"{CC.highlight_word('top to bottom')}. Just use the {CC.highlight_word('top most')} {_HL.gate} as base and " \
        f"{CC.highlight_word('put the lower')} one(s) into it."

    SerialGates = \
        f"Applying two {_HL.gates} in series is as easy as {CC.highlight_word('multiplying')} two matrices.\n" \
        f"Let's consider an {_HL.gate_x} at q0 followed by a {_HL.gate_cx} at q0 (=control), q1 (=target). So we " \
        f"compute a {_HL.matrix_4x4} for the {_HL.gate_x} (see {_HL.kronecker} and then " \
        f"{CC.highlight_word('multiply')} the matrix of the {_HL.gate_cx} {CC.highlight_word('from the left')}:\n" \
        f"    |00> |01> |10> |11>         |00> |01> |10> |11>         |00> |01> |10> |11>\n" \
        f"|00>  1    0    0    0      |00>  0    1    0    0      |00>  0    1    0    0 \n" \
        f"|01>  0    0    0    1   *  |01>  1    0    0    0   =  |01>  0    0    1    0 \n" \
        f"|10>  0    0    1    0      |10>  0    0    0    1      |10>  0    0    0    1 \n" \
        f"|11>  0    1    0    0      |11>  0    0    1    0      |11>  1    0    0    0 \n" \
        f"\n" \
        f"If we take a look at the result's column {CC.highlight_word('|00>')} we can see that the resulting matrix " \
        f"{_HL.transforms} this state to {CC.highlight_word('|11>')} as expected (i.e., X negates q0=0 to q0=1 and " \
        f"then CX negates q1=0 to q1=1 since it's control (q0) is 1).\n" \
        f"Again, in general the {_HL.order} of multiplication matters. At first glance it may seem counter-intuitive " \
        f"that the {_HL.gates} are aligned from {CC.highlight_word('left to right')} in the {_HL.circuit} but have " \
        f"to be {CC.highlight_word('multiplied')} from {CC.highlight_word('right to left')}. But in the " \
        f"{_HL.mat_vec_mul} the {_HL.input_stv} is on the right side while for the {_HL.circuit} the input is on the " \
        f"left. Therefore in both cases simply the gate/matrix {CC.highlight_word('closer')} to the input is " \
        f"considered first."

    # todo: the split after "collapse to" seems to think that |00> refers to a color code, hence adding // without closing //?
    Amplitudes = \
        f"Let's consider the following {_HL.state_vector}:\n" \
        "|00>  0.707  \n" \
        "|01>  0.707  \n" \
        "|10>    0    \n" \
        "|11>    0    \n" \
        f"From {_HL.ket_notation} we know that both q0=q1=0 and q0=0, q1=1 have an {_HL.amplitude} of 0.707 while " \
        f"it's 0 for the remaining qubit configuration (q0=1, q1=0 and q0=q0=1).\n" \
        f"To transform the amplitude into a probability we have to take it's absolute value squared: abs(0.707)^2 = " \
        f"0.5 which corresponds to 50%. Just as expected this {_HL.state_vector} {_HL.collapses} 50% of the time to " \
        f"|00> and the remaining 50% to |01>. It can never collapse to |10> or |11> because these configurations " \
        f"have an amplitude of 0.\n" \
        f"Since the probabilities need to add up to 1 (100%), the sum of the " \
        f"{CC.highlight_word('squared absolute values')} of a {CC.highlight_object('Quantum StateVector')} also need " \
        f"to be 1.\n" \
        f"In general {_HL.quantum_state}s are described by {CC.highlight_word('complex values')} so unlike in the " \
        f"example above it is very important to not forget to apply the absolute operator before squaring."

    Riddle = \
        f"{_HL.riddles} are very similar to {_HL.puzzles}, yet a bit different. They also shows you a " \
        f"{_HL.target_state} you need to {_HL.reach} to solve it but you {_HL.cannot} {_HL.try_} it " \
        f"{_HL.arbitrary} {_HL.often}. They have predefined {_HL.number_of_times} you can {_HL.edit} your " \
        f"{_HL.circuit} before they get {_HL.unstable}. Unstable {_HL.riddles} have a 50% chance to {_HL.vanish} " \
        f"together with their {_HL.reward} whenever you update your {_HL.circuit}."

    Challenge = \
        "TODO"

    BossFight = \
        f"Now it's getting {_HL.serious}! You are fighting against {_HL.bell}. For the {_HL.state} you need to reach " \
        f"to defeat Bell your two {_HL.qubits} will always have to be the same: either {_HL.both0} or {_HL.both1}.\n" \
        f"This is called {_HL.entanglement}.\n\n" \
        "Good luck!"  # todo make more generic

    Game = \
        f"QRogue is a game about {_HL.quantum_computing}. You will explore " \
        f"Levels and Expeditions and solve {_HL.puzzles} with the help of {_HL.quantum_gates} to reach even " \
        f"farther places of the universe.\n"

    Pause = \
        "In the Pause Menu you can do several things:\n" \
        f"{_HL.continue_} - Leave the Pause Menu and continue where you stopped.\n" \
        f"{_HL.restart} - Restart the current level.\n" \
        f"{_HL.save} - Save your game. Remember that your progress is only saved level-wise.\n" \
        f"{_HL.help_} - If you ever feel stuck and don't remember how certain stuff in the game works open " \
        f"the manual and we will try to help you.\n" \
        f"{_HL.options} - Configure some options of the game, like font size or coloring.\n" \
        f"{_HL.exit_} - Exit the current level."

    Options = "7"
    Welcome = Game + \
        "\nBut before you can explore the universe you have to complete a trainings program.\n" \
        f"Now close this dialog by pressing {_HL.action_keys}. Select {_HL.start_journey} with " \
        f"{_HL.navigation_keys} and confirm your selection with {_HL.action_keys} to begin!"

    def __init__(self, text: str):
        self.__text = text

    @property
    def text(self) -> str:
        return self.__text


def get_filtered_help_texts() -> List[HelpText]:
    return [
        HelpText.Game,
        HelpText.Controls,
        #HelpText.Pause,
        HelpText.Fight, HelpText.Ket, HelpText.ParallelGates, HelpText.SerialGates, HelpText.Amplitudes,
        #HelpText.Riddle, #HelpText.Challenge,
    ]


def load_help_text(type_: str) -> Optional[str]:
    for key in HelpText:
        if key.name.lower() == type_.lower():
            return key.text
    return None
