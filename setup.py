from setuptools import setup, find_packages

setup(
    name="arXivScraper",
    version="1.0",
    packages=find_packages,
    install_requires=[
        "PySide6",
        "arxiv",
        "sqlite3"
    ]
)