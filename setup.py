from setuptools import setup

setup(
    name='game_solvers',
    version='0.1',
    description='A python package to solve various logic games',
    author='Joey Wynne',
    author_email='joey.wynne@btinternet.com',
    packages=["game_solvers"],
    install_requires=[
        "numpy==2.3.1",
        "matplotlib==3.10.3",
        "pandas==2.3.1",
        "bs4==0.0.2",
        "requests==2.32.4",
        "lxml==6.0.0",
        "rich==14.1.0",
        "tqdm==4.67.1",
        "setuptools==80.9.0",
    ],
)