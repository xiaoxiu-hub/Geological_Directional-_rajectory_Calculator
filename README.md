# Geological Directional Trajectory Calculator (地质导向轨迹计算器)

这是一个基于 **Python 3** 和 **PySide2** 开发的轻量级地质导向与井眼轨迹解算桌面应用。项目遵循 Model-View 架构设计，实现了高精度的轨迹推导、真厚度计算、角差计算、A点预测及视倾角转换功能。

---

## 1. 功能特性

### 1.1 井眼轨迹级联解算 (Minimum Curvature Method)
* 采用石油工业标准的 **最小曲率半径法** 进行空间三维轨迹积分。
* 支持多测点递推计算。当修改中间任意测点数据时，模型会自动触发后续所有相关测点数据的级联重算，并通过信号刷新界面，无需手动刷新。
* 支持第一行自动相对于隐式井口基准（0, 0, 160.26）进行起步计算。

### 1.2 钻遇地层真厚度计算与线性插值
* 实现了四种地质边界（上倾下切、上倾上切、下倾下切、下倾上切）下的真实地层厚度计算。
* 针对用户输入的任意特征点井深，系统会在轨迹数据表中自动检索相邻测点并执行**线性插值算法**，自动推导出对应的垂深及闭合位移，再代入真厚度公式。

### 1.3 角差计算和A点预测
* 解决上倾/下倾地层中，从当前井斜到目标井斜所需的斜深、狗腿度及视平移距离。
* 预测在上倾或下倾地层条件下，靶点（A点）的预测垂深。

### 1.4 真倾角转视倾角
* 实现三维空间内地质真倾角向二维垂直剖面内视倾角的投影转换。

---

## 2. 软件工程架构

本程序在设计上注重解耦与动态适应性：
1. **动态相对路径**：使用 `pathlib` 在运行时动态解析项目根路径，彻底消除硬编码死路径，确保代码在不同环境下的无缝协作。
2. **UI 与逻辑解耦**：利用 `QUiLoader` 动态解析 Qt Designer 生成的 `.ui`（XML）文件，避免频繁编译 `.py` 界面文件的繁琐步骤。
3. **MVC 模式实践**：通过重写 `QAbstractTableModel` 托管复杂的级联计算逻辑，使数据模型（Model）和显示界面（View）彻底分离。

```text
地质导向轨迹计算器/
├── main.py                     # 应用程序主入口，负责环境自适应配置与事件循环启动
├── requirements.txt            # 项目依赖清单
├── core/
│   ├── __init__.py
│   └── paths.py                # 动态路径自适应工具
└── ui/
    ├── __init__.py
    ├── main_window.py          # 主窗体路由控制器
    ├── forms/                  # XML 界面资源库 (存放 .ui 文件)
    │   ├── main.ui             # 主框架布局
    │   ├── true_thickness.ui   # 轨迹数据表与真厚度解算界面
    │   ├── mainwindow.ui       # 角差计算与A点预测界面
    │   └── true_dip.ui         # 真倾角转视倾角界面
    └── views/                  # 业务逻辑控制层
        ├── __init__.py
        ├── true_thickness.py   # 真厚度计算与线性插值路由
        ├── angle_diff.py       # 角差预测计算业务逻辑
        └── true_dip.py         # 投影倾角转换业务逻辑
```

---

## 3. 数学物理模型与核心公式 (无格式冲突版)

为了保证多平台复制不产生排版冲突，以下公式均采用标准纯文本 (ASCII) 格式排版，可直接应用于学术报告与 PPT：

### 3.1 井眼轨迹解算：最小曲率半径法 (Minimum Curvature Method)
对于相邻两测点 i-1 和 i，对应井深为 MD，井斜角为 I，方位角为 A：

```text
1. 计算井段长度 dMD：
   dMD = MD_i - MD_(i-1)

2. 空间夹角（狗腿角） delta 计算：
   cos(delta) = cos(I_i - I_(i-1)) - sin(I_(i-1)) * sin(I_i) * [1 - cos(A_i - A_(i-1))]
   delta = arccos(cos(delta))  (单位：弧度)

3. 曲率校正系数 RF：
   当 delta <= 10^-4 rad 时：
   RF = 1.0
   当 delta > 10^-4 rad 时：
   RF = (2 / delta) * tan(delta / 2)

4. 坐标累加计算：
   * 垂深：TVD_i = TVD_(i-1) + [dMD / 2 * (cos(I_(i-1)) + cos(I_i)) * RF]
   * 南北：N_i = N_(i-1) + [dMD / 2 * (sin(I_(i-1)) * cos(A_(i-1)) + sin(I_i) * cos(A_i)) * RF]
   * 东西：E_i = E_(i-1) + [dMD / 2 * (sin(I_(i-1)) * sin(A_(i-1)) + sin(I_i) * sin(A_i)) * RF]
   * 闭合位移：CD_i = sqrt(N_i^2 + E_i^2)
   * 闭合方位：CA_i = arctan2(E_i, N_i)
   * 狗腿度 (DLS)：DLS_i = (delta * 180) / (pi * dMD) * 30  (单位：度/30米)
```

### 3.2 钻遇地层真厚度计算公式
基于垂深差 AD = |TVD_2 - TVD_1|，闭合位移差 DB = |CD_2 - CD_1|，地层倾角为 theta：

```text
* 上倾下切 / 下倾上切：
  AE = (AD + tan(theta) * DB) * cos(theta)
* 上倾上切 / 下倾下切：
  AE = (AD - tan(theta) * DB) * cos(theta)

注：若特征点输入井深非实测点，系统会自动在表格中检索上下邻近点并执行线性插值，解算出对应的 TVD_f 和 CD_f 再代入公式。
```

### 3.3 A 点预测与视倾角转换
```text
* 角差公式上倾井（解算斜深与狗腿度）：
  平均井斜 theta_avg = (I_1 + I_2) / 2
  地层井眼夹角 phi = (90 + theta_dip) - theta_avg
  斜深 MD = H_vertical / sin(phi)
  狗腿度 DLS = 30 * (I_2 - I_1) / MD
  剩余视平移 = cos(|90 - theta_avg|) * MD

* 角差公式下倾井（解算斜深与狗腿度）：
  地层井眼夹角 phi = (90 - theta_dip) - theta_avg
  (其余解算方法与上倾井一致)

* 预测垂深（上倾井）：
  TVD_predicted = TVD_current + [T_true / cos(theta_dip)] - [L_horizontal * tan(theta_dip)]

* 预测垂深（下倾井）：
  TVD_predicted = TVD_current + [T_true / cos(theta_dip)] + [L_horizontal * tan(theta_dip)]

* 真视倾角转换：
  tan(alpha) = tan(beta) * cos(theta) => alpha = arctan(tan(beta) * cos(theta))
```

---

## 4. 环境要求与安装运行

### 4.1 环境要求
* 操作系统：Windows 10 / 11 
* Python 版本：Python 3.8 及以上（兼容 Python 3.14）

### 4.2 依赖安装
在项目根目录下，使用 pip 安装所需的运行依赖：
```bash
pip install -r requirements.txt
```

### 4.3 启动程序
```bash
python main.py
```
