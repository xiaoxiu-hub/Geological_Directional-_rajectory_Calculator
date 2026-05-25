# main.py
import sys
import os
import PySide2
plugins_path = os.path.join(os.path.dirname(PySide2.__file__), 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugins_path

from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt
from ui.main_window import MainWindow


def main():
    # 针对 Win 11 高分屏/缩放屏进行自适应缩放优化（避免界面模糊）
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # noinspection PyArgumentList
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()