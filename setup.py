import os

from setuptools import setup

README_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Readme.md')
with open(README_PATH) as readme_file:
	README = readme_file.read()

# https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56
setup(
	name='qrogue',  # Name of package folder
	packages=[
		'qrogue',
		'qrogue.util',
		'qrogue.util.config',
		'qrogue.game',
		'qrogue.game.logic',
		'qrogue.game.logic.base',
		'qrogue.game.logic.collectibles',
		'qrogue.game.logic.actors',
		'qrogue.game.logic.actors.controllables',
		'qrogue.game.logic.actors.puzzles',
		'qrogue.game.world',
		'qrogue.game.world.navigation',
		'qrogue.game.world.tiles',
		'qrogue.game.world.map',
		'qrogue.game.world.dungeon_generator',
		'qrogue.game.world.dungeon_generator.dungeon_parser',
		'qrogue.game.world.dungeon_generator.wave_function_collapse',
		'qrogue.graphics',
		'qrogue.graphics.rendering',
		'qrogue.graphics.popups',
		'qrogue.graphics.widgets',
		'qrogue.management',
	],
	package_data={"data": ["qrogue/data"]},
	include_package_data=True,
	version='0.8',
	license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
	description='QRogue is a modernized Quantum Computing take of the classical game Rogue.',
	long_description=README,
	long_description_content_type="text/markdown",
	author='Michael Artner',
	author_email='michael.artner@hotmail.de',
	url='https://github.com/7Magic7Mike7/Qrogue',
	download_url='https://github.com/7Magic7Mike7/Qrogue/releases/tag/0.8',  # link to Release on GitHub
	keywords=['Quantum Computing', 'Gamification', 'Video Game', 'PyCUI'],
	install_requires=[
		'py-cui==0.1.4',
		'numpy==1.22.3',
		'qiskit==0.34.2',
		'qiskit-aer==0.12.2',
		'antlr4-python3-runtime==4.13.2',
	],
	classifiers=[
		'Development Status :: 3 - Alpha',  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
		'Intended Audience :: Education',
		'Intended Audience :: Science/Research',
		'Topic :: Games/Entertainment :: Puzzle Games',
		'Programming Language :: Python :: 3.8',
	],
	entry_points={
		'console_scripts': ['qrogue=qrogue.qrogue:start_qrogue'],
	}
)
