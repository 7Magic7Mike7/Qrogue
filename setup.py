from distutils.core import setup
setup(
  name = 'Qrogue',         # Name of package folder
  packages = ['Qrogue'],   # Same as "name"
  version = '0.2.1',
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository  # todo
  description = 'Qrogue is a modernized Quantum Computing take of the classical game Rogue. It can be played in a '
                'terminal and aims to improve your understanding of Quantum Computing',
  author = 'Michael Artner',
  author_email = 'michael.artner@jku.at',
  url = 'https://github.com/7Magic7Mike7/Qrogue',
  download_url = '',    # link to Release on GitHub # todo
  keywords = ['Quantum Computing', 'Gamification', 'Video Game', 'PyCUI'],
  install_requires=[
          'py-cui',
          'qiskit',
    # todo
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
    'Intended Audience :: Anyone interested in Quantum Computing',
    'Topic :: Quantum Computing :: Gamification',
    'License :: OSI Approved :: MIT License',   # Again, pick a license # todo
    'Programming Language :: Python :: 3.8',
  ],
)