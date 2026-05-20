from typing import TypedDict, Literal, Optional

DecisionStatus = Literal['Optional', 'Forbidden']
ShortageRuleType = Literal['First come, first served', 'Customer priority', 'Proportional']
ProductFamilyType = Literal['PET', 'Pack 1L', 'Capsule']

class CustomerInfo(TypedDict):
    """单条顾客记录的结构（字段名与含义）。"""
    name: str
    product_range: dict[str, DecisionStatus]
    market_share: float  # 荷兰市场份额（%），如 2.0 表示 2.0%
    Number_of_stores: int  # 荷兰门店数量
    Value_for_money: bool


# 顾客列表：每条记录为一个字典（按游戏界面字段整理）
# 新增顾客时，复制 Super 的字典结构并修改各字段即可
CUSTOMERS: list[CustomerInfo] = [
    {
        "name": "Super",
        "product_range": {
            "Fressie Orange 1 liter": "Optional",
            "Fressie Orange/Mango 1 liter": "Optional",
            "Fressie Orange/Mango+C 1L": "Optional",
            "Fressie Orange PET": "Optional",
            "Fressie Orange/C-power PET": "Optional",
            "Fressie Orange/Mango PET": "Optional",
            "Frespressie Orange": "Optional",
            "Frespressie Mango": "Optional",
            "Frespressie Orange/Mango": "Optional",
        },
        "market_share": 5.0,
        "Number_of_stores": 80,
        "Value_for_money": False,
    },
    {
        "name": "Convi",
        "product_range": {
            "Fressie Orange 1 liter": "Forbidden",
            "Fressie Orange/Mango 1 liter": "Forbidden",
            "Fressie Orange/Mango+C 1L": "Forbidden",
            "Fressie Orange PET": "Optional",
            "Fressie Orange/C-power PET": "Optional",
            "Fressie Orange/Mango PET": "Optional",
            "Frespressie Orange": "Optional",
            "Frespressie Mango": "Optional",
            "Frespressie Orange/Mango": "Optional",
        },
        "market_share": 12.0,
        "Number_of_stores": 210,
        "Value_for_money": True,
    },
    {
        "name": "SAVE",
        "product_range": {
            "Fressie Orange 1 liter": "Optional",
            "Fressie Orange/Mango 1 liter": "Optional",
            "Fressie Orange/Mango+C 1L": "Optional",
            "Fressie Orange PET": "Optional",
            "Fressie Orange/C-power PET": "Optional",
            "Fressie Orange/Mango PET": "Optional",
            "Frespressie Orange": "Forbidden",
            "Frespressie Mango": "Forbidden",
            "Frespressie Orange/Mango": "Forbidden",
        },
        "market_share": 8.0,
        "Number_of_stores": 140,
        "Value_for_money": True,
    },
    {
        "name": "Online",
        "product_range": {
            "Fressie Orange 1 liter": "Forbidden",
            "Fressie Orange/Mango 1 liter": "Forbidden",
            "Fressie Orange/Mango+C 1L": "Forbidden",
            "Fressie Orange PET": "Forbidden",
            "Fressie Orange/C-power PET": "Forbidden",
            "Fressie Orange/Mango PET": "Forbidden",
            "Frespressie Orange": "Optional",
            "Frespressie Mango": "Optional",
            "Frespressie Orange/Mango": "Optional",
        },
        "market_share": 2.0,
        "Number_of_stores": 10,
        "Value_for_money": False,
    },
]

# 按顾客名称快速查询：CUSTOMERS_BY_NAME["Super"]
CUSTOMERS_BY_NAME: dict[str, CustomerInfo] = {
    Customer["name"]: customer for customer in CUSTOMERS
}


class Customer_contract:
    def __init__(self, supplier_name, contract_index, service_level, shelf_life,
                 order_deadline, trade_unit, payment_term, promotional_pressure,
                 promotion_horizon, vmi_supplier):
        '''basic information'''
        self.supplier_name = supplier_name

        '''supplier contract information'''
        self.contract_index = contract_index
        self.service_level = service_level
        self.shelf_life = shelf_life
        self.order_deadline = order_deadline
        self.payment_term = payment_term
        self.trade_unit = trade_unit
        self.promotional_pressure = promotional_pressure
        self.promotion_horizon =promotion_horizon

        '''collaboration projects'''
        self.vmi_supplier = vmi_supplier

    def update_terms(self,
                     service_level: Optional[float] = None,
                     shelf_life: Optional[float] = None,
                     order_deadline: Optional[int] = None,
                     trade_unit: Optional[str] = None,
                     payment_term: Optional[int] = None,
                     promotional_pressure: Optional[float] = None,
                     promotion_horizon: Optional[int] = None,
                     vmi_supplier: Optional[bool] = None):
        """
        显式修改合同条款。
        只有当传入的参数不为 None 时，才会覆盖原有的决策值。
        """
        if service_level is not None:
            self.service_level = service_level
        if shelf_life is not None:
            self.shelf_life = shelf_life
        if order_deadline is not None:
            self.order_deadline = order_deadline
        if trade_unit is not None:
            self.trade_unit = trade_unit
        if payment_term is not None:
            self.payment_term = payment_term
        if promotional_pressure is not None:
            self.promotional_pressure = promotional_pressure
        if promotion_horizon is not None:
            self.promotion_horizon = promotion_horizon
        if vmi_supplier is not None:
            self.vmi_supplier = vmi_supplier


class OrderManagement:
    def __init__(self, shortage_rule: ShortageRuleType = 'First come, first served'):
        """
        订单管理模块
        shortage_rule: 短缺规则，默认为 'First come, first served'
        """
        self.shortage_rule: ShortageRuleType = shortage_rule

    def update_shortage_rule(self, rule: ShortageRuleType):
        """修改短缺规则"""
        self.shortage_rule = rule



class CategoryManagement:
    def __init__(self, customers_list: list[CustomerInfo]):
        """
        品类管理模块
        customers_list: 传入现有的 CUSTOMERS 列表
        """
        # 决策矩阵：仅针对原本是 'Optional' 的产品初始化为决策变量（默认上架: True，下架: False）
        self.matrix: dict[str, dict[str, bool]] = {}

        for customer in customers_list:
            cust_name = customer["name"]
            self.matrix[cust_name] = {}

            for prod_name, status in customer["product_range"].items():
                if status == "Optional":
                    self.matrix[cust_name][prod_name] = True

    def set_category_decision(self, customer_name: str, product_name: str, is_selected: bool):
        """
        品类管理进行勾选或取消
        """
        if customer_name in self.matrix and product_name in self.matrix[customer_name]:
            self.matrix[customer_name][product_name] = is_selected
        else:
            print(f"产品 [{product_name}] 在客户 [{customer_name}] 的合同中不可选，无法做品类管理决策。")

    def sync_to_customers(self, customers_list: list[CustomerInfo]):
        """
        将品类管理的决策结果，反向同步/更新到 CUSTOMERS 数据结构中
        游戏最终提交决策时，如果品类管理没勾选，该产品对该客户的状态会变成 'Forbidden'
        """
        for customer in customers_list:
            cust_name = customer["name"]
            if cust_name in self.matrix:
                for prod_name in list(customer["product_range"].keys()):
                    if prod_name in self.matrix[cust_name]:
                        is_selected = self.matrix[cust_name][prod_name]
                        customer["product_range"][prod_name] = "Optional" if is_selected else "Forbidden"


class FamilyForecastItem:
    def __init__(self, base_demand: float, change_percent: float = 0.0):
        """
        单种大类的预测数据
        base_demand: 基础周需求量 (Weekly demand (liters))
        change_percent: 调整比例，如 0.05 表示 +5%，-0.1 表示 -10%
        """
        self.base_demand: float = base_demand
        self.change_percent: float = change_percent  # 对应界面的百分比调整

    @property
    def expected_demand(self) -> float:
        """计算得到的预期周需求量 (Expected demand per week)"""
        return self.base_demand * (1.0 + self.change_percent)


class DemandForecast:
    def __init__(self):
        """需求预测模块（以荷兰市场 The Netherlands 为例）"""
        # 初始化各个大类的基础数据
        self.forecasts: dict[ProductFamilyType, FamilyForecastItem] = {
            "PET": FamilyForecastItem(base_demand=69559),
            "Pack 1L": FamilyForecastItem(base_demand=188619),
            "Capsule": FamilyForecastItem(base_demand=4361),
        }

    def adjust_forecast(self, family: ProductFamilyType, change_percent: float):
        """
        调整某大类的预测百分比
        family: 大类名称
        change_percent: 调整浮点数，例如输入 5 表示 +5%（代码中转为 0.05）
        """
        if family in self.forecasts:
            self.forecasts[family].change_percent = change_percent / 100.0

    def get_expected_demand(self, family: ProductFamilyType) -> float:
        """获取某一类的最终预期需求量"""
        return self.forecasts[family].expected_demand if family in self.forecasts else 0.0