from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
from core.paths import FORMS_DIR

# 导入子页面 (只保留一次，去除重复)
from ui.views.true_thickness import TrueThicknessView
from ui.views.angle_diff import AngleDiffView
from ui.views.true_dip import TrueDipView


class MainWindow:
    def __init__(self):
        ui_file_path = FORMS_DIR / "main.ui"
        ui_file = QFile(str(ui_file_path))
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        self._init_sub_pages()
        self._connect_signals()

    def _init_sub_pages(self):
        # 实例化子页面 (去除了重复代码)
        self.page_true_thickness = TrueThicknessView()
        self.page_angle_diff = AngleDiffView()
        self.page_true_dip = TrueDipView()

        # 添加到 stackedWidget
        self.ui.stackedWidget.addWidget(self.page_true_thickness)  # index 1
        self.ui.stackedWidget.addWidget(self.page_angle_diff)  # index 2
        self.ui.stackedWidget.addWidget(self.page_true_dip)  # index 3

    def _connect_signals(self):
        # 绑定按钮信号
        self.ui.btn_true_thickness.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.btn_angle_diff.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.btn_true_dip.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))

    def show(self):
        self.ui.show()