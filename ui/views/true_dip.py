# -*- coding: utf-8 -*-
import math
from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
from core.paths import FORMS_DIR


class TrueDipView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = None
        self._load_ui()
        # noinspection PyUnresolvedReferences
        self.ui.btn_calc.clicked.connect(self.calculate)

    def _load_ui(self):
        ui_file_path = FORMS_DIR / "true_dip.ui"
        ui_file = QFile(str(ui_file_path))
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

    def calculate(self):
        try:
            beta = float(self.ui.input_true_dip.text())
            theta = float(self.ui.input_theta.text())

            # 公式: tan(α) = tan(β) * cos(θ)
            rad_beta = math.radians(beta)
            rad_theta = math.radians(theta)

            tan_alpha = math.tan(rad_beta) * math.cos(rad_theta)
            alpha = math.degrees(math.atan(tan_alpha))

            self.ui.output_apparent_dip.setText(f"{alpha:.4f}")
        except ValueError:
            self.ui.output_apparent_dip.setText("输入错误")