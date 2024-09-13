# setup.py
from setuptools import setup

# Read the contents of requirements.txt
with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="tvhelper",
    version="0.1",
    py_modules=["tvhelper"],
    install_requires=required,  # Install dependencies from requirements.txt
    entry_points={
        'console_scripts': [
            'tvhelper=tvhelper:main',
        ],
    },
)
