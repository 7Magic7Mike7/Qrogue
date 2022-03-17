from distutils.core import setup
setup(
  name = 'qrogue',         # Name of package folder
  packages = ['qrogue',
              'qrogue.util',
              'qrogue.game',
                'qrogue.game.logic',
                  'qrogue.game.logic.collectibles',
                  'qrogue.game.logic.actors',
                    'qrogue.game.logic.actors.controllables', 'qrogue.game.logic.actors.puzzles',
                'qrogue.game.world',
                  'qrogue.game.world.navigation', 'qrogue.game.world.tiles', 'qrogue.game.world.map',
                  'qrogue.game.world.dungeon_generator',
                    'qrogue.game.world.dungeon_generator.dungeon_parser',
                    'qrogue.game.world.dungeon_generator.world_parser',
              'qrogue.graphics',
                'qrogue.graphics.rendering',
                'qrogue.graphics.popups',
                'qrogue.graphics.widgets',
              'qrogue.management',
              ],
  package_data={"data": ["qrogue/data"]},
  version = '0.2.1.8',
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Qrogue is a modernized Quantum Computing take of the classical game Rogue. It can be played in a '
                'terminal and aims to improve your understanding of Quantum Computing',
  author = 'Michael Artner',
  author_email = 'michael.artner@jku.at',
  url = 'https://github.com/7Magic7Mike7/Qrogue',
  download_url = 'https://github.com/7Magic7Mike7/Qrogue/releases/tag/0.2.1.7',    # link to Release on GitHub
  keywords = ['Quantum Computing', 'Gamification', 'Video Game', 'PyCUI'],
  install_requires=[
          'py-cui',
          'qiskit',
          'antlr4-python3-runtime',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'Topic :: Games/Entertainment :: Puzzle Games',
    'Programming Language :: Python :: 3.8',
  ],
)