from setuptools import setup, find_packages

setup(
    name="scrubpy",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "click",
        "rich",
        "InquirerPy",
    ],
    entry_points={
        "console_scripts": [
            "scrubpy = scrubpy.cli:main",
        ],
    },
)
