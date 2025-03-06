import ArxivScraper
from PySide6 import QtWidgets
import sys


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ArxivScraper.FinderWindow()
    window.resize(1500, 800)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()