# -*- coding: utf-8 -*-
import math
from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile, Qt
from core.paths import FORMS_DIR


class AngleDiffView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = None
        self._load_ui()
        self.setup_styles()
        self.connect_signals()

    def _load_ui(self):
        ui_file_path = FORMS_DIR / "angle_diff.ui"
        ui_file = QFile(str(ui_file_path))
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.ui.setWindowFlags(Qt.Widget)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

    def setup_styles(self):
        pass

    def connect_signals(self):
        # 绑定各个子模块的计算按钮
        self.ui.angleUpCalcBtn.clicked.connect(self.calculate_angle_up)
        self.ui.angleDownCalcBtn.clicked.connect(self.calculate_angle_down)
        self.ui.aUpCalcBtn.clicked.connect(self.calculate_a_up)
        self.ui.aDownCalcBtn.clicked.connect(self.calculate_a_down)

    @staticmethod
    def get_float(line_edit):
        try:
            return float(line_edit.text())
        except ValueError:
            return 0.0

    def calculate_angle_up(self):
        current_incl = self.get_float(self.ui.angleUpCurrentIncl)
        target_incl = self.get_float(self.ui.angleUpTargetIncl)
        vertical_thick = self.get_float(self.ui.angleUpVerticalThick)
        formation_dip = self.get_float(self.ui.angleUpFormationDip)

        avg_incl = (current_incl + target_incl) / 2
        phi = (90 + formation_dip) - avg_incl
        phi_rad = phi * math.pi / 180
        sin_phi = math.sin(phi_rad)

        md = vertical_thick / sin_phi if sin_phi != 0 else 0
        dogleg = 30 * (target_incl - current_incl) / md if md != 0 else 0

        angle_for_shift = abs(90 - avg_incl) * math.pi / 180
        apparent_shift = math.cos(angle_for_shift) * md

        self.ui.angleUpMd.setText(f"{md:.0f}")
        self.ui.angleUpDogleg.setText(f"{dogleg:.1f}")
        self.ui.angleUpApparentShift.setText(f"{apparent_shift:.0f}")

    def calculate_angle_down(self):
        current_incl = self.get_float(self.ui.angleDownCurrentIncl)
        target_incl = self.get_float(self.ui.angleDownTargetIncl)
        vertical_thick = self.get_float(self.ui.angleDownVerticalThick)
        formation_dip = self.get_float(self.ui.angleDownFormationDip)

        avg_incl = (current_incl + target_incl) / 2
        phi = (90 - formation_dip) - avg_incl
        phi_rad = phi * math.pi / 180
        sin_phi = math.sin(phi_rad)

        md = vertical_thick / sin_phi if sin_phi != 0 else 0
        dogleg = 30 * (target_incl - current_incl) / md if md != 0 else 0

        angle_for_shift = abs(90 - avg_incl) * math.pi / 180
        apparent_shift = math.cos(angle_for_shift) * md

        self.ui.angleDownMd.setText(f"{md:.0f}")
        self.ui.angleDownDogleg.setText(f"{dogleg:.1f}")
        self.ui.angleDownApparentShift.setText(f"{apparent_shift:.0f}")

    def calculate_a_up(self):
        true_thick = self.get_float(self.ui.aUpTrueThick)
        formation_dip = self.get_float(self.ui.aUpFormationDip)
        current_vd = self.get_float(self.ui.aUpCurrentVd)
        horizontal_dist = self.get_float(self.ui.aUpHorizontalDist)

        angle_rad = formation_dip * math.pi / 180
        cos_angle = math.cos(angle_rad)
        tan_angle = math.tan(angle_rad)

        predicted_vd = current_vd + (true_thick / cos_angle) - (horizontal_dist * tan_angle)
        self.ui.aUpPredictedVd.setText(f"{predicted_vd:.1f}")

    def calculate_a_down(self):
        true_thick = self.get_float(self.ui.aDownTrueThick)
        formation_dip = self.get_float(self.ui.aDownFormationDip)
        current_vd = self.get_float(self.ui.aDownCurrentVd)
        horizontal_dist = self.get_float(self.ui.aDownHorizontalDist)

        angle_rad = formation_dip * math.pi / 180
        cos_angle = math.cos(angle_rad)
        tan_angle = math.tan(angle_rad)

        predicted_vd = current_vd + (true_thick / cos_angle) + (horizontal_dist * tan_angle)
        self.ui.aDownPredictedVd.setText(f"{predicted_vd:.1f}")