from qrogue.test.test_util import DummySelectionWidget
from qrogue.test import test_util as tu


def test():
    options = ["X Gate", "H Gate", "X Gate", "CX Gate",]# "Remove", "-Back-"]
    sel = DummySelectionWidget(2, True, False)
    sel.set_data(data=(
        options,
        [tu.true_callback] * len(options)
    ))
    sel.get_dummy_widget().selected = True

    def render():
        sel.render()
        print(sel.widget.get_title())

    while True:
        render()
        cin = input("")
        if cin == "w":
            sel.up()
        elif cin == "d":
            sel.right()
        elif cin == "s":
            sel.down()
        elif cin == "a":
            sel.left()
        else:
            break


test()
