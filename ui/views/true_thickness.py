# ui/views/true_thickness.py
import math
from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile, Qt
from core.paths import FORMS_DIR
from ui.models.trajectory_model import TrajectoryTableModel


class TrueThicknessView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = None
        self.model = None
        self._load_ui()
        self._setup_table()
        self._connect_signals()

    def _load_ui(self):
        ui_file_path = FORMS_DIR / "true_thickness.ui"
        ui_file = QFile(str(ui_file_path))
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

    def _setup_table(self):
        # 绑定重构后的计算模型
        self.model = TrajectoryTableModel(self)
        self.ui.table_trajectory.setModel(self.model)

    def _connect_signals(self):
        # noinspection PyUnresolvedReferences
        self.ui.btn_calculate.clicked.connect(self.calculate_true_thickness)

    def _interpolate_feature_point(self, md_str):
        """
        根据用户输入的特征点井深，在表格数据中执行自动线性插值
        """
        try:
            target_md = float(md_str)
        except ValueError:
            return 0.0, 0.0

        # 收集表格中所有已计算的有效测点数据 (提取 井深-col1, 垂深-col4, 闭合位移-col8)
        valid_points = []
        for r in range(self.model.rowCount()):
            idx_md = self.model.index(r, 1)
            idx_tvd = self.model.index(r, 4)
            idx_closure = self.model.index(r, 8)

            md = self.model.data(idx_md, Qt.DisplayRole)
            tvd = self.model.data(idx_tvd, Qt.DisplayRole)
            closure = self.model.data(idx_closure, Qt.DisplayRole)

            if md is not None and tvd is not None and closure is not None:
                valid_points.append((md, tvd, closure))

        if not valid_points:
            return 0.0, 0.0

        # 按井深排序
        valid_points.sort(key=lambda x: x[0])

        # 边界情况处理
        if target_md <= valid_points[0][0]:
            return valid_points[0][1], valid_points[0][2]
        if target_md >= valid_points[-1][0]:
            return valid_points[-1][1], valid_points[-1][2]

        # 线性插值计算
        for i in range(len(valid_points) - 1):
            p1 = valid_points[i]
            p2 = valid_points[i + 1]
            if p1[0] <= target_md <= p2[0]:
                fraction = (target_md - p1[0]) / (p2[0] - p1[0]) if p2[0] != p1[0] else 0.0
                tvd = p1[1] + fraction * (p2[1] - p1[1])
                closure = p1[2] + fraction * (p2[2] - p1[2])
                return tvd, closure

        return 0.0, 0.0

    def calculate_true_thickness(self):
        try:
            dip_mode = self.ui.combo_dip_mode.currentText()
            formation_dip = float(self.ui.input_formation_dip.text() or 0)
            theta = math.radians(formation_dip)

            # 自动在表格中插值计算出两点的真实 TVD 和 闭合位移
            f1_tvd, f1_closure = self._interpolate_feature_point(self.ui.input_f1_md.text())
            f2_tvd, f2_closure = self._interpolate_feature_point(self.ui.input_f2_md.text())

            ad = abs(f2_tvd - f1_tvd)
            closure_diff = abs(f2_closure - f1_closure)

            ae = 0.0
            if dip_mode == "上倾下切":
                ae = (ad + math.tan(theta) * closure_diff) * math.cos(theta)
            elif dip_mode == "上倾上切":
                ae = (ad - math.tan(theta) * closure_diff) * math.cos(theta)
            elif dip_mode == "下倾下切":
                ae = (ad - math.tan(theta) * closure_diff) * math.cos(theta)
            elif dip_mode == "下倾上切":
                ae = (ad + math.tan(theta) * closure_diff) * math.cos(theta)

            self.ui.output_true_thickness.setText(f"{ae:.4f}")

        except ValueError:
            self.ui.output_true_thickness.setText("输入错误")