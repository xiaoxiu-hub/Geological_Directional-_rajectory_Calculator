# ui/models/trajectory_model.py
import math
from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex


class TrajectoryTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.headers = ["序号", "井深", "井斜", "方位", "垂深", "南北坐标", "东西坐标", "闭合方位", "闭合位移",
                        "视平位移", "狗腿度"]

        # 显式声明类型：内部数据可能包含 float 或 None
        self._data: list[list[float | None]] = []

        # 初始化 20 行空数据，预填序号，输出列初始化为 0.0
        for i in range(20):
            row: list[float | None] = [float(i + 1), None, None, None, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            self._data.append(row)

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

    def flags(self, index):
        if index.column() in [1, 2, 3]:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.column() in [1, 2, 3]:
            try:
                self._data[index.row()][index.column()] = float(value)
                self._recalculate_from(index.row())

                # 【核心修正】：通知 QTableView 刷新从当前行起、至右下角终点的所有受影响格子
                top_left = self.index(index.row(), 0)
                bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
                self.dataChanged.emit(top_left, bottom_right)

                return True
            except ValueError:
                return False
        return False

    def _recalculate_from(self, start_row):
        for i in range(start_row, self.rowCount()):
            curr = self._data[i]

            # 如果当前行的 井深/井斜/方位 任意一个未填，则不计算该行及后续行
            if curr[1] is None or curr[2] is None or curr[3] is None:
                continue

            if i == 0:
                # 序号1 (第1行) 相对于隐式井口 (0.00, 0.00, 初始方位) 进行增量计算
                md1, i1, a1 = 0.0, 0.0, math.radians(curr[3])
                md2, i2, a2 = curr[1], math.radians(curr[2]), math.radians(curr[3])
                dmd = md2 - md1

                cos_delta = math.cos(i2 - i1) - math.sin(i1) * math.sin(i2) * (1 - math.cos(a2 - a1))
                delta = math.acos(max(-1.0, min(1.0, cos_delta)))
                rf = (2 / delta * math.tan(delta / 2)) if delta > 1e-4 else 1.0

                d_tvd = rf * dmd / 2 * (math.cos(i1) + math.cos(i2))
                d_n = rf * dmd / 2 * (math.sin(i1) * math.cos(a1) + math.sin(i2) * math.cos(a2))
                d_e = rf * dmd / 2 * (math.sin(i1) * math.sin(a1) + math.sin(i2) * math.sin(a2))

                curr[4] = d_tvd  # 垂深
                curr[5] = d_n  # 南北坐标
                curr[6] = d_e  # 东西坐标
                curr[7] = math.degrees(math.atan2(curr[6], curr[5]))
                curr[8] = math.sqrt(curr[5] ** 2 + curr[6] ** 2)
                curr[10] = (math.degrees(delta) / dmd * 30) if dmd != 0 else 0.0
                continue

            # 序号 > 1 的行，相对于上一行进行增量计算
            prev = self._data[i - 1]
            if prev[1] is None or prev[2] is None or prev[3] is None:
                continue

            md1, i1, a1 = prev[1], math.radians(prev[2]), math.radians(prev[3])
            md2, i2, a2 = curr[1], math.radians(curr[2]), math.radians(curr[3])
            dmd = md2 - md1

            cos_delta = math.cos(i2 - i1) - math.sin(i1) * math.sin(i2) * (1 - math.cos(a2 - a1))
            delta = math.acos(max(-1.0, min(1.0, cos_delta)))
            rf = (2 / delta * math.tan(delta / 2)) if delta > 1e-4 else 1.0

            d_tvd = rf * dmd / 2 * (math.cos(i1) + math.cos(i2))
            d_n = rf * dmd / 2 * (math.sin(i1) * math.cos(a1) + math.sin(i2) * math.cos(a2))
            d_e = rf * dmd / 2 * (math.sin(i1) * math.sin(a1) + math.sin(i2) * math.sin(a2))

            prev_tvd = prev[4] if prev[4] is not None else 0.0
            prev_n = prev[5] if prev[5] is not None else 0.0
            prev_e = prev[6] if prev[6] is not None else 0.0

            curr[4] = prev_tvd + d_tvd
            curr[5] = prev_n + d_n
            curr[6] = prev_e + d_e
            curr[7] = math.degrees(math.atan2(curr[6], curr[5]))
            curr[8] = math.sqrt(curr[5] ** 2 + curr[6] ** 2)
            curr[10] = (math.degrees(delta) / dmd * 30) if dmd != 0 else 0.0