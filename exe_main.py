import os.path

from qrogue import qrogue

base_path = os.path.dirname(__file__)

user_dir = os.path.join(base_path, "USER")
if not os.path.exists(user_dir):
    os.mkdir(user_dir)

data_path = os.path.join(base_path, "data")

print(os.path.dirname(__file__))
qrogue.start_game(data_folder=data_path, user_data_folder=user_dir)
