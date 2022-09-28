import sys

from qrogue import qrogue

if __name__ == "__main__":
    return_code = qrogue.start_qrogue()
    sys.exit(return_code)
