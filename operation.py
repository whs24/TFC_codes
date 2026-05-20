#!usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time: 2026/5/21 00:51
# @Author: 偷走月亮的猫

from typing import TypedDict, Dict, List, Literal

# ==========================================
# 1. 静态常量与结构体定义 (Constants & TypedDict)
# ==========================================

class MixerInfo(TypedDict):
    mixer_type: str
    tech_batch_min_liters: float  # 技术最小批次（升）
    max_lot_size_liters: float  # 最大批次大小（升）
    yearly_costs: float  # 年固定成本 (€)
    costs_per_hour: float  # 每小时变动成本 (€/hour)
    investment: float  # 投资额 (€)
    run_time_per_batch_hours: float  # 每批次单次搅拌运行时间（小时）
    cleantime: float


class BottlingLineInfo(TypedDict):
    line_type: str
    capacity_liters_per_hour: float  # 产能（升/小时）
    number_of_operators: int  # 标配永久操作工人数
    operator_costs_per_annum: float  # 单个操作工年薪 (€)
    costs_flexible_labor_per_hour: float  # 临时工/加班每小时成本 (€/hour)
    yearly_costs: float  # 产线年固定折旧/维护成本 (€)
    investment: float  # 投资额 (€)
    formula_changeover_time_hours: float  # 换配方配模时间（小时）
    size_changeover_time_hours: float  # 换包装尺寸配模时间（小时）
    tolerances: Literal['Narrow', 'Middle', 'Wide']  # 灌装精度公差
    startup_productivity_loss: float  # 开机启动生产力损失（%），如 0.15 表示 15%


# 游戏中可供选择的混合器资产池
MIXERS: dict[str, MixerInfo] = {
    "Fruitmix MQ": {
        "mixer_type": "MegaChurn 20",
        "tech_batch_min_liters": 8000.0,
        "max_lot_size_liters": 12000.0,
        "yearly_costs": 62500.00,
        "costs_per_hour": 135.00,
        "investment": 312500.00,
        "run_time_per_batch_hours": 2.0,
        "cleantime": 2.0
    },
    "MegaChurn 20": {
        "mixer_type": "MegaChurn 20",
        "tech_batch_min_liters": 15000.0,
        "max_lot_size_liters": 20000.0,
        "yearly_costs": 75000.00,
        "costs_per_hour": 160.00,
        "investment": 375000.00,
        "run_time_per_batch_hours": 2.0,
        "cleantime": 3.0
    },
    "FMM 4000": {
        "mixer_type": "FMM 4000",
        "tech_batch_min_liters": 1500.0,
        "max_lot_size_liters": 4200.0,
        "yearly_costs": 30000.00,
        "costs_per_hour": 100.00,
        "investment": 100000.00,
        "run_time_per_batch_hours": 2.0,
        "cleantime": 1.0
    }
}

# 游戏中可供选择的灌装线资产池
BOTTLING_LINES: dict[str, BottlingLineInfo] = {
    "TopSpeed 1": {
        "line_type": "TopSpeed 1",
        "capacity_liters_per_hour": 3000.0,
        "number_of_operators": 4,
        "operator_costs_per_annum": 40000.00,
        "costs_flexible_labor_per_hour": 42.00,
        "yearly_costs": 115000.00,
        "investment": 575000.00,
        "formula_changeover_time_hours": 3.0,
        "size_changeover_time_hours": 4.0,
        "tolerances": "Narrow",
        "startup_productivity_loss": 0.15,
    },
    "MultiFlex 2": {
        "line_type": "MultiFlex 2",
        "capacity_liters_per_hour": 1200.0,
        "number_of_operators": 4,
        "operator_costs_per_annum": 40000.00,
        "costs_flexible_labor_per_hour": 42.00,
        "yearly_costs": 50000.00,
        "investment": 100000.00,
        "formula_changeover_time_hours": 1.0,
        "size_changeover_time_hours": 2.0,
        "tolerances": "Wide",
        "startup_productivity_loss": 0.04,
    },
    "Swiss Fill 2": {
        "line_type": "Swiss Fill 2",
        "capacity_liters_per_hour": 2800.0,
        "number_of_operators": 5,
        "operator_costs_per_annum": 40000.00,
        "costs_flexible_labor_per_hour": 42.00,
        "yearly_costs": 100000.00,
        "investment": 500000.00,
        "formula_changeover_time_hours": 2.0,
        "size_changeover_time_hours": 3.0,
        "tolerances": "Middle",
        "startup_productivity_loss": 0.10,
    }
}


# ==========================================
# 2. 运营决策与管理逻辑类 (Decision Classes)
# ==========================================

class OperationsDecisionManager:
    def __init__(self):
        """
        初始化运营角色需要决定的所有决策变量 (对应游戏面板)
        """
        # --- 2.1 供应链与入库质检 ---
        self.supplier_inspection: Dict[str, bool] = {}  # 键:供应商名, 值:是否需要原材料检验
        self.intake_time: int = 0 # 进货时间窗口 (如 Standard / 24h)

        # --- 2.2 仓库容量与永久雇员数 ---
        self.inbound_pallet_locations: int = 0  # 入库托盘个数（固体材料库容）
        self.inbound_tank_count: int = 0  # 入库储罐数量（液体材料库容）
        self.inbound_warehouse_permanent_staff: int = 0  # 进货仓库永久雇员人数

        self.outbound_pallet_locations: int = 0  # 出货仓库托盘数（产成品库容）
        self.outbound_warehouse_permanent_staff: int = 0  # 出货仓库永久工作人数

        # --- 2.3 混合阶段 (Mixer) 决策 ---
        self.active_mixers: List[str] = []  # 选中的混合器列表 (例如: ["MegaChurn 20"])
        self.raw_material_mixer_map: Dict[str, str] = {}  # 哪种原材料在哪个混合器里搅拌 {"Orange": "MegaChurn 20"}

        # --- 2.4 包装与产线 (Bottling Line) 决策 ---
        self.active_lines: List[str] = []  # 启用的产线列表 (例如: ["TopSpeed 1", "MultiFlex 2"])
        self.line_speedup: Dict[str, bool] = {}  # 产线是否加速生产 {"TopSpeed 1": False}
        self.sku_line_assignment: Dict[str, str] = {}  # 每一种产品/样品分配在哪条产线上生产

        # --- 2.5 质量与技术选择 ---
        self.use_preventative_maintenance: bool = False  # 装瓶阶段是否采用预防性检测
        self.use_blow_molding: bool = False  # 是否在车间自行吹瓶
        self.use_track_and_trace: bool = False  # 是否开启Track/Trace（追踪与溯源系统）

        # --- 2.6 换产频次（通过排产逻辑或计划得出，供财务模块计算换模成本） ---
        self.line_changeovers: Dict[str, int] = {}  # 每条产线总换产次数 {"TopSpeed 1": 5}

    def set_warehouse_and_staff(self, inbound_staff: int, outbound_staff: int,
                                in_pallets: int, in_tanks: int, out_pallets: int):
        """批量更新仓储容量与永久工人数"""
        self.inbound_warehouse_permanent_staff = inbound_staff
        self.outbound_warehouse_permanent_staff = outbound_staff
        self.inbound_pallet_locations = in_pallets
        self.inbound_tank_count = in_tanks
        self.outbound_pallet_locations = out_pallets

    def assign_production(self, sku_name: str, line_name: str):
        """将某种SKU指定到特定的灌装线"""
        if line_name in BOTTLING_LINES:
            self.sku_line_assignment[sku_name] = line_name
        else:
            print(f"警告: 产线 {line_name} 不存在于资产池中。")


class OperationsCostCalculator:
    """
    运营成本与产能核算模块 (对接 global.py 中的科目定义)
    """

    def __init__(self, decision: OperationsDecisionManager):
        self.dec = decision

    def calculate_mixer_fixed_costs(self) -> float:
        """计算混合器固定的年折旧/维护费用 (对应 global.py 中的 production_costs_mixer_fixed_costs)"""
        total_fixed = 0.0
        for m_name in self.dec.active_mixers:
            if m_name in MIXERS:
                total_fixed += MIXERS[m_name]["yearly_costs"]
        return total_fixed

    def calculate_bottling_fixed_costs(self) -> float:
        """计算灌装线固定的年费用与常驻操作工成本"""
        total_fixed = 0.0
        total_operator_costs = 0.0

        for l_name in self.dec.active_lines:
            if l_name in BOTTLING_LINES:
                line_info = BOTTLING_LINES[l_name]
                total_fixed += line_info["yearly_costs"]
                # 标配工人成本
                total_operator_costs += line_info["number_of_operators"] * line_info["operator_costs_per_annum"]

        return total_fixed

    def calculate_investment_machines(self) -> float:
        """计算设备总投资额，用于影响最终 ROI (对应 global.py 中的 investment_machines)"""
        total_inv = 0.0
        # 统计启用的混合器投资
        for m_name in self.dec.active_mixers:
            if m_name in MIXERS:
                total_inv += MIXERS[m_name]["investment"]
        # 统计启用的灌装线投资
        for l_name in self.dec.active_lines:
            if l_name in BOTTLING_LINES:
                total_inv += BOTTLING_LINES[l_name]["investment"]
        return total_inv

    # TODO: 后续可以基于排产时长、换模次数(line_changeovers)和加速状态(line_speedup)，
    # 结合 costs_flexible_labor_per_hour 与 costs_per_hour，进一步编写变动生产成本计算逻辑