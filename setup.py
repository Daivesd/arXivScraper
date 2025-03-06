from setuptools import setup

setup(
    name="arXivScraper",
    version="1.0",
    description="A nice description",
    author=".",
    packages=["arXivScraper"],
    install_requires=[
        "PySide6",
        "arxiv",
        "sqlite3"
    ],
    entry_points={
        "gui_scripts": [
            "arXivScraper = arXivScraper.main:main",
        ]
    },
)