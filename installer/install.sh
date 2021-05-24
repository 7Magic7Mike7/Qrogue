#!/bin/bash

ENV_PATH="../.env_qrogue"
DATA_PATH="../game_data"

echo "[Qrogue] Creating a new venv..."

FULL_PATH=$(realpath "$0")
cd "$(dirname "${FULL_PATH}")" || exit 202
mkdir -p ${ENV_PATH}
python3 -m venv ${ENV_PATH}

if [ $? ]; then
	echo "[Qrogue] venv successfully created"
	echo "[Qrogue] Activating venv..."
	source ${ENV_PATH}/bin/activate

	if [ $? ]; then
		echo "[Qrogue] Downloading and installing required packages..."
		pip3 install -q -r requirements_linux.txt

		if [ $? ]; then
			echo "[Qrogue] Creating config files..."

			touch qrogue.config
			realpath "${ENV_PATH}" > qrogue.config
			realpath "${DATA_PATH}" >> qrogue.config
			mkdir -p "${DATA_PATH}"
			#mkdir -p ${DATA_PATH}/logs
			#mkdir -p ${DATA_PATH}/keylogs
			#mkdir -p ${DATA_PATH}/screenprints

			if [ $? ]; then
				echo
				echo "[Qrogue] Done!"
				echo "[Qrogue] You can play now my executing play_qrogue.sh!"
				exit 0
			else
				echo "[Qrogue] ERROR: Could not create qrogue.config!"
				exit 4
			fi
		else
			echo "[Qrogue] ERROR: Requirements could not be installed!"
			exit 1
		fi
	else
		echo "[Qrogue] ERROR: Could not activate venv"
		exit 2
	fi
else
	echo "[Qrogue] Creating venv failed. Please check if you fulfill all prerequisites (in prerequisites.txt)!"
	exit 3
fi