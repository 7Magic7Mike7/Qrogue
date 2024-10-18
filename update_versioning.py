import os
import sys


def validate_version(new_version: str):
    if "." not in new_version:
        return False

    parts = new_version.split(".")
    # every part except the last needs to be a number
    for i in range(len(parts) - 1):
        try:
            int(parts[i])
        except:
            return False
    # the last part just needs to start with a number
    return parts[len(parts) - 1][0].isdigit()


def update(new_version: str):
    __update_readme(new_version)
    __update_setup(new_version)
    __update_config(new_version)


def __update_readme(new_version: str):
    readme = os.path.join(".", "Readme.md")

    # update version occurrence in headline
    with open(readme, 'r') as file:
        data = file.read()

        prefix = "Qrogue v"
        start = data.find(prefix)
        end = data.find("#", start + len(prefix))
        data = f"{data[:start]}{prefix}{new_version} {data[end:]}"

    with open(readme, 'w') as file:
        file.write(data)


def __update_setup(new_version: str):
    setup = os.path.join(".", "setup.py")

    with open(setup, 'r') as file:
        data = file.read()

        # first update the pypi version
        prefix = "version=\'"
        start = data.find(prefix)
        end = data.find("\'", start + len(prefix))
        data = f"{data[:start]}{prefix}{new_version}{data[end:]}"

        # second update the github release url
        prefix = "https://github.com/7Magic7Mike7/Qrogue/releases/tag/"
        start = data.find(prefix)
        end = data.find("\'", start + len(prefix))
        data = f"{data[:start]}{prefix}{new_version}{data[end:]}"

    with open(setup, 'w') as file:
        file.write(data)


def __update_config(new_version: str):
    config = os.path.join("qrogue", "util", "config", "config.py")

    with open(config, 'r') as file:
        data = file.read()

        prefix = "__VERSION = \"v"
        start = data.find(prefix)
        end = data.find("\"", start + len(prefix))
        data = f"{data[:start]}{prefix}{new_version}{data[end:]}"

    with open(config, 'w') as file:
        file.write(data)


if __name__ == "__main__":
    new_version_ = sys.argv[1]
    if validate_version(new_version_):
        update(new_version_)
        print("Successfully updated the version.")
    else:
        print("ERROR! Specified version has wrong format.")
