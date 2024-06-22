import os
import unittest

from qrogue.game.logic.collectibles import InstructionManager
from qrogue.game.target_factory import BossFactory
from qrogue.util import PathConfig, StvDifficulty
from qrogue.util.util_functions import cur_datetime, int_to_fixed_len_str, time_diff


class ValidationTests(unittest.TestCase):
    def test_validate(self):
        self.assertTrue(InstructionManager.validate(), "InstructionManager is invalid!")
        self.assertTrue(StvDifficulty.validate(), "StvDifficulty is invalid!")
        self.assertTrue(BossFactory.validate(), "BossFactory is invalid!")

    # todo: do all kinds of validation here so we can use it for "qrogue --validate" for the study's installation check?

    def test_str_format(self):
        length = 5
        value = 1458
        text = (f"Test value of length={length}: " + f"{{0:0{length}d}}")
        print(text)
        print(text.format(value))
        print()
        print(int_to_fixed_len_str(value, length))

    def test_general(self):
        start = cur_datetime()
        j = 0
        for i in range(100_000):
            j += i ** 2
        print(j)
        end = cur_datetime()

        diff = time_diff(start, end)
        """
        a = complex(real=0, imag=0.707)
        print(f"abs({a}) = {abs(a)}")
        print(f"{a}^2 = {a**2}")
        print(f"abs({a})^2 = {abs(a)**2}")

        assert complex(1) == 1, "no"
        assert complex(0, 1) != 1, "no"
        print()
        
        angle = math.pi * 2
        rot = [[math.e**(complex(0, -1) * angle/2), 0], [0, math.e**(complex(0, 1) * angle/2)]]
        for row in rot:
            for val in row:
                re, im = round(val.real, 2), round(val.imag, 2)
                if im >= 0: print(f"{re}+{im}j", end="")
                else: print(f"{re}{im}j", end="")
                print("   ", end="")
            print()
        """

        print("; ".join([str(inst) for inst in [1, 2, 3, 4, 5]]))

    def test_filtering(self):
        file_path = PathConfig.user_data_path(os.path.join("logs", "28092023_113726_seed479093" + ".qrlog"))
        filtered_path = PathConfig.user_data_path(os.path.join("logs", "filtered.qrlog"))

        with open(file_path, 'rt') as log_file:
            with open(filtered_path, "wt") as filtered_file:
                for line in log_file:
                    if line.startswith("{PyCUI}"):
                        continue

                    if "Starting puzzle" in line:
                        filtered_file.write("\n\n")

                    filtered_file.write(line)

                    if "Finished level" in line:
                        filtered_file.write("\n\n\n\n\n")

    def test_versioning(self):
        from importlib.metadata import version
        import numpy as np
        import py_cui
        import qiskit
        import sys

        versioning_incorrect = False

        # check for python 3.8 or 3.9
        if sys.version_info.major != 3 or sys.version_info.minor not in [8, 9]:
            print(f"Your Python version is {sys.version_info.major}.{sys.version_info.minor} but we only support 3.8 "
                  f"and 3.9!")
            versioning_incorrect = True
        else:
            print("Python version is fine.")

        # check numpy version
        np_version = np.version.version.split(".")
        if len(np_version) < 3:
            print(f"Invalid version of numpy: {np.version.version}")
            versioning_incorrect = True
        elif np_version[0] == "1":
            np_minor, np_micro = int(np_version[1]), int(np_version[2])
            if np_minor == 22 and np_micro == 3 or np_minor == 26 and np_micro == 0:
                print("Numpy version is fine.")
            elif 22 < np_minor < 26 or np_minor == 22 and np_micro > 3:
                print("Numpy version should be fine. If you want to be sure though, we recommend to up- or downgrade "
                      "to either 1.22.3 or 1.26.0")
            else:
                print(f"Unsupported version of numpy: {np.version.version}")
                versioning_incorrect = True
        else:
            print(f"Unsupported version of numpy: {np.version.version}")
            versioning_incorrect = True

        # check py-cui version
        if py_cui.__version__ in ["0.1.4", "0.1.6"]:
            print("py-cui version is fine.")
        elif py_cui.__version__ == "0.1.5":
            print("py-cui version should be fine. If you want to be sure though, we recommend to up- or downgrade "
                  "to either 0.1.4 or 0.1.6")
        else:
            print(f"Unsupported version of py-cui: {py_cui.__version__}")
            versioning_incorrect = True

        # check qiskit version
        if qiskit.version.VERSION.startswith("0."):
            qiskit_version = qiskit.version.VERSION.split(".")
            qiskit_minor, qiskit_micro = int(qiskit_version[1]), int(qiskit_version[2])
            if qiskit_minor == 19 and qiskit_micro == 2 or qiskit_minor == 44 and qiskit_micro == 1:
                print("Qiskit version is fine.")
            elif qiskit_minor == 19 and qiskit_micro > 2 or 19 < qiskit_minor < 44 or \
                    qiskit_minor == 44 and qiskit_micro < 1:
                print("qiskit version should be fine. If you want to be sure though, we recommend to up- or downgrade "
                      "to either 0.19.2 or 0.44.1")
            else:
                print(f"Unsupported version of qiskit: {qiskit.version.VERSION}")
                versioning_incorrect = True
        else:
            print(f"Unsupported version of qiskit {qiskit.version.VERSION}")
            versioning_incorrect = True

        try:
            antl_version = version('antlr4-python3-runtime').split(".")
            antl_major, antl_minor = int(antl_version[0]), int(antl_version[1])
            if antl_major == 4 and (antl_minor == 10 or antl_minor == 12):
                print("antlr4-python3-runtime version is fine.")
            elif antl_major == 4 and antl_minor == 11:
                print("antlr4-python3-runtime version should be fine. If you want to be sure though, we recommend to "
                      "up- or downgrade to either 4.10 or 4.12")
        except:
            print("Cannot check version of antlr4. Please use 'pip list' and check yourself.")

        if versioning_incorrect:
            print("Please consider using supported versions for Python and modules because otherwise the game likely "
                  "won't work.")


if __name__ == '__main__':
    unittest.main()
