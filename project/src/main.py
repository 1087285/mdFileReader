"""
main.py - エントリーポイント
QApplication を生成し MainWindow を起動する。
"""
import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("mdFileReader")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
