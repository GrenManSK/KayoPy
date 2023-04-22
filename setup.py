from setuptools import setup
from setuptools import find_packages
from kayopy.kayopy import VERSION, AUTHOR

setup(
    name='kayopy',
    version=VERSION,
    description='kayopy',
    author=AUTHOR,
    install_requires=['bs4'],
    packages=find_packages(exclude=('tests*', 'testing*')),
    entry_points={
        'console_scripts': [
            'kayopy = kayopy.kayopy:main',
        ],
    }
)
