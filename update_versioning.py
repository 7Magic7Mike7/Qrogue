import os
import sys

new_version = sys.argv[1]


def validate_version():
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


def update():
    __update_readme()
    __update_setup()
    __update_config()


def __update_readme():
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


def __update_setup():
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


def __update_config():
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
    if validate_version():
        update()
        print("Successfully updated the version.")
    else:
        print("ERROR! Specified version has wrong format.")
