# 地质导向轨迹计算器 - 学术报告与项目开发指南 (README)

> **面向团队分工**：
> - **实验报告撰写人**：可直接复制 [第 3 节：数学物理模型] 的公式及推导，以及 [第 4 节] 的系统设计。
> - **PPT 汇报制作人**：可直接引用 [第 2 节：技术亮点] 及 [第 4 节] 的架构框图作为幻灯片结构。
> - **流程图绘制人**：可根据 [第 5 节：业务控制流程] 的 Mermaid 拓扑图直接在 Visio 或 Draw.io 中绘图。

---

## 1. 项目简介
地质导向（Geosteering）是石油钻井工程中控制钻头在薄储层中穿行的核心技术。本项目基于 **Python 3.14 (向下兼容) + PySide2 (Qt5)** 架构，设计并实现了一款轻量化、高精度的地质导向轨迹计算器。
系统主要包含三大功能：
1. **真厚度计算**：支持批量井眼轨迹数据的“最小曲率半径法”自动解算，并利用特征点自动线性插值解算四种地质边界（上倾下切、上倾上切、下倾下切、下倾上切）下的真实地层厚度。
2. **角差计算和A点预测**：解算上/下倾地层中的斜深、狗腿度、视平移，以及预测靶点（A点）的垂深。
3. **真倾角转视倾角**：实现三维倾角向二维垂直剖面视倾角的投影转换。

---

## 2. 系统核心技术亮点 (PPT 汇报核心)
*   **Model-View 彻底解耦**：采用 `QAbstractTableModel` 重新托管表格数据，界面只负责呈现，计算完全由底层 Model 控制。
*   **级联自动重绘 (Cascade Recalculation)**：当修改某一测点的井深、井斜或方位角时，模型自动触发对当前行及后续所有行的级联重新计算，并通过 `dataChanged` 信号进行区域动态刷新，告别手动重绘。
*   **动态环境自适应**：利用 `pathlib` 动态推导工程路径，彻底废除死路径；采用 `QUiLoader` 动态加载 `.ui` 蓝图，实现前端设计（Designer）与后端逻辑分离。

---

## 3. 数学物理模型与核心公式 (实验报告核心)

### 3.1 井眼轨迹解算：最小曲率半径法 (Minimum Curvature Method)
设相邻两测点为 $i-1$ 和 $i$，其井深、井斜角、方位角分别为 $(MD_{i-1}, I_{i-1}, A_{i-1})$ 和 $(MD_i, I_i, A_i)$。
1. **计算井段长 $\Delta MD$**：
   $$\Delta MD = MD_i - MD_{i-1}$$

2. **计算空间两点夹角（狗腿角） $\Delta$**：
   $$\cos(\Delta) = \cos(I_i - I_{i-1}) - \sin(I_{i-1}) \cdot \sin(I_i) \cdot [1 - \cos(A_i - A_{i-1})]$$

3. **计算曲率校正系数 $RF$ (Ratio Factor)**：
   $$RF = \begin{cases} 1.0, & \Delta \le 10^{-4} \text{ rad} \\ \frac{2}{\Delta} \tan\left(\frac{\Delta}{2}\right), & \Delta > 10^{-4} \text{ rad} \end{cases}$$

4. **计算坐标增量**：
   *   垂深增量：$\Delta TVD = \frac{\Delta MD}{2} \cdot (\cos I_{i-1} + \cos I_i) \cdot RF$
   *   南北增量：$\Delta N = \frac{\Delta MD}{2} \cdot (\sin I_{i-1} \cos A_{i-1} + \sin I_i \cos A_i) \cdot RF$
   *   东西增量：$\Delta E = \frac{\Delta MD}{2} \cdot (\sin I_{i-1} \sin A_{i-1} + \sin I_i \sin A_i) \cdot RF$

5. **派生指标解算**：
   *   累积垂深：$TVD_i = TVD_{i-1} + \Delta TVD$
   *   累积坐标：$N_i = N_{i-1} + \Delta N$，$E_i = E_{i-1} + \Delta E$
   *   闭合位移：$CD_i = \sqrt{N_i^2 + E_i^2}$
   *   闭合方位：$CA_i = \arctan2(E_i, N_i)$
   *   狗腿度 (DLS)：$DLS_i = \frac{\Delta \cdot 180}{\pi \cdot \Delta MD} \times 30 \quad (\text{deg/30m})$

### 3.2 钻遇地层真厚度计算模型
基于垂深差 $AD = |TVD_2 - TVD_1|$，闭合位移差 $DB = |CD_2 - CD_1|$，地层倾角为 $\theta$：
*   **上倾下切**：$AE = (AD + \tan(\theta) \cdot DB) \cdot \cos(\theta)$
*   **上倾上切**：$AE = (AD - \tan(\theta) \cdot DB) \cdot \cos(\theta)$
*   **下倾下切**：$AE = (AD - \tan(\theta) \cdot DB) \cdot \cos(\theta)$
*   **下倾上切**：$AE = (AD + \tan(\theta) \cdot DB) \cdot \cos(\theta)$

*注：若输入的特征点井深在测点之间，采用线性插值法确定该点的 $TVD$ 与 $CD$。*

### 3.3 角差计算与 A 点预测模型
设 $I_1$ 为当前井斜，$I_2$ 为目标井斜，$H$ 为垂厚，$\theta_{dip}$ 为地层倾角。平均井斜 $\theta_{avg} = \frac{I_1 + I_2}{2}$。
*   **夹角公式上倾井**：
   *   地层与井眼夹角：$\phi = (90^\circ + \theta_{dip}) - \theta_{avg}$
   *   斜深：$MD = \frac{H}{\sin(\phi)}$
   *   狗腿度：$DLS = \frac{30 \cdot (I_2 - I_1)}{MD}$
   *   视平移：$apparent\_shift = \cos(|90^\circ - \theta_{avg}|) \cdot MD$
*   **夹角公式下倾井**：
   *   地层与井眼夹角：$\phi = (90^\circ - \theta_{dip}) - \theta_{avg}$
   *   *(其余项与上倾井公式一致)*
*   **预测垂深上倾井**：
   $$TVD_{predicted} = TVD_{current} + \frac{T_{true}}{\cos(\theta_{dip})} - L_{horizontal} \cdot \tan(\theta_{dip})$$
*   **预测垂深下倾井**：
   $$TVD_{predicted} = TVD_{current} + \frac{T_{true}}{\cos(\theta_{dip})} + L_{horizontal} \cdot \tan(\theta_{dip})$$

### 3.4 真倾角转视倾角模型
设 $\beta$ 为地层真倾角，$\theta$ 为井轨迹方位与地层真倾向的夹角，$\alpha$ 为视倾角：
$$\tan(\alpha) = \tan(\beta) \cdot \cos(\theta) \implies \alpha = \arctan(\tan(\beta) \cdot \cos(\theta))$$

---

## 4. 系统拓扑与文件结构 (实验报告/PPT)

### 4.1 目录树
```text
地质导向轨迹计算器/
├── main.py                     # 应用程序入口
├── requirements.txt            # 项目依赖清单
├── core/
│   ├── __init__.py
│   └── paths.py                # 动态路径解析工具
└── ui/
    ├── __init__.py
    ├── main_window.py          # 主窗体路由控制器
    ├── forms/                  # XML 设计资源库
    │   ├── main.ui             # 主框架 UI
    │   ├── true_thickness.ui   # 真厚度计算 UI
    │   └── true_dip.ui         # 真倾角解算 UI
    └── views/                  # 页面业务控制层
        ├── __init__.py
        ├── true_thickness.py   # 轨迹计算及插值算法逻辑
        ├── angle_diff.py       # 角差计算与A点预测逻辑
        └── true_dip.py         # 倾角投影转换计算逻辑
4.2 模块依赖框图 (PPT 结构图)
[ main.py ]  ---(启动)---> [ ui/main_window.py ] (加载 main.ui)
                                   |
                      +------------+------------+
                      | (切换选项卡加载子视图)    |
                      v                         v
           [ ui/views/true_thickness.py ]   [ ui/views/angle_diff.py ]
                      |                                 |
              (绑定 QAbstractModel)               (计算逻辑解算)
                      v
       [ ui/models/trajectory_model.py ]
              |
         (最小曲率法计算)
5. 业务控制流程图 (流程图绘制核心)
graph TD
    A[用户在 QTableView 中修改测点数据] --> B{修改的是否为前3列?}
    B -- 否 --> C[拒绝编辑/仅作显示]
    B -- 是 --> D[触发 setData 信号]
    D --> E[调用内层 _recalculate_from 方法]
    E --> F[确定起点行 start_row]
    F --> G[i = start_row]
    G --> H{i == 0 ?}
    H -- 是 --> I[相对于隐式井口 0,0,0 进行累加计算]
    H -- 否 --> J[获取前一测点 i-1 数据进行空间曲率计算]
    I --> K[更新当前行 i 的 TVD/南北/东西/闭合位移/狗腿度等数据]
    J --> K
    K --> L[i = i + 1]
    L --> M{i < rowCount ?}
    M -- 是 --> G
    M -- 否 --> N[生成 topLeft 和 bottomRight 索引范围]
    N --> O[发射 dataChanged 信号]
    O --> P[QTableView 局部区域强制重绘, 刷新显示]
5.2 真厚度自动线性插值与解算流程 (True Thickness)
graph TD
    A[输入特征点 1/2 井深 MD] --> B[点击计算真厚度]
    B --> C[扫描数据表, 筛选所有有效计算测点数据]
    C --> D{列表是否为空?}
    D -- 是 --> E[返回 0.0, 终止计算]
    D -- 否 --> F[按井深大小排序]
    F --> G{输入 MD 范围检测}
    G -- 小于等于首测点 --> H[截断: 直接取首测点的 TVD 与闭合位移]
    G -- 大于等于尾测点 --> I[截断: 直接取尾测点的 TVD 与闭合位移]
    G -- 处于两测点之间 --> J[定位相邻两测点 p1(MD1) 与 p2(MD2)]
    J --> K[线性计算比例系数 fraction = (target - MD1) / (MD2 - MD1)]
    K --> L[TVD_f = TVD1 + fraction * (TVD2 - TVD1)]
    L --> M[Closure_f = Clo1 + fraction * (Clo2 - Clo1)]
    H --> N[获取两点参数差值: ad = |TVD_f2 - TVD_f1|, closure_diff = |Clo_f2 - Clo_f1|]
    I --> N
    M --> N
    N --> O{获取倾角模式}
    O -- 上倾下切 --> P[ae = (ad + tan(theta) * closure_diff) * cos(theta)]
    O -- 上倾上切 --> Q[ae = (ad - tan(theta) * closure_diff) * cos(theta)]
    O -- 下倾下切 --> R[ae = (ad - tan(theta) * closure_diff) * cos(theta)]
    O -- 下倾上切 --> S[ae = (ad + tan(theta) * closure_diff) * cos(theta)]
    P --> T[真厚度 ae 格式化输出]
    Q --> T
    R --> T
    S --> T
6. 环境安装与部署
6.1 运行依赖
操作系统：Windows 10/11
Python 环境：3.8 - 3.14+ (推荐 Python 3.10 及以上)
核心库：PySide2==5.15.2.1
6.2 部署步骤
解压项目源码包。
在项目根目录下打开终端，执行环境初始化安装：
pip install -r requirements.txt
启动应用程序：
python main.py


