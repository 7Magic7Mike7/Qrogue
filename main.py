#D:\Programs\anaconda3\envs\Qrogue
# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import random
import py_cui
from widgets.circuit_widget import CircuitWidget
from widgets.qrogue_pycui import *


def print_hi(name="?"):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Strg+F8 to toggle the breakpoint.


def test(label):
    r = random.randint(a=0, b=10)
    label.set_title(f"Random number = {r}")


def test2(label):
    r = random.randint(a=0, b=10)
    label.set_title(f" number = {r}")


def old_code():
    root.enable_logging("./log.txt", logging_level=py_cui.logging.INFO)
    print("Renderer: ", root._renderer)
    print("Renderer: ", type(root._renderer))

    ROW_SPAN = 3
    # tb_qubits = root.add_block_label('Qubits', 1, 0, row_span=ROW_SPAN, center=True)
    # tb_gen = root.add_block_label('Generator', 1, 1, row_span=ROW_SPAN, center=False)
    # tb_circ = root.add_block_label('Circuit', 1, 2, row_span=ROW_SPAN, column_span=5, center=False)
    # root.add_label('Welcome', 0, 0)

    # tb_qubits.set_title("q0\nq1\nq2")
    # tb_gen.set_title("-- H --\n-- H --\n-- H --")
    # tb_circ.set_title("----- I ----\n----- I ----\n----- I ----")

    # tb_gen.toggle_border()

    # root.add_circuit_widget("Test", 1, 1)
    # add_circ_widg(root, "Test", 1, 1)
    # root.add_my_label("Test", 7, 7)

    print("Renderer: ", root._renderer)


root = QroguePyCUI()
root.start()
