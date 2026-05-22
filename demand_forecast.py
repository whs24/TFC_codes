#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time: 2026/5/22
# @Author: Demand Forecast Module

import os
import csv
import numpy as np
from typing import TypedDict, Dict, List, Optional, Literal
from sales import CUSTOMERS, Customer_contract


class ProductDemand(TypedDict):
    """产品需求数据结构"""
    product_name: str
    customer_name: str
    base_demand: float        # 基础周需求量（单位）
    pattern_factor: float     # 模式因子（季节性波动）
    promotional_factor: float # 促销影响因子
    final_demand: float       # 最终预测需求量


PromotionalPressureLevel = Literal['Benchmark', 'Low', 'Middle', 'High']
"""促销压力等级类型"""


class DemandForecastEngine:
    """
    需求预测引擎
    
    基于历史需求数据和促销决策，预测下一个运营周期的需求量。
    
    数据来源：
    - pattern_data: 整体需求波动模式数据（用于提取季节性和周期性波动）
    - value_data: 按客户-产品的基准需求量数据
    
    核心特性：
    1. 从 pattern 数据中提取季节性波动模式
    2. 从 value 数据中获取各客户-产品的基础需求量
    3. 根据促销压力等级计算促销影响
    4. 支持按客户、产品、产品大类多维度查询
    """
    
    # 促销压力对应的需求增长范围（百分比）
    PROMOTIONAL_FACTORS: Dict[PromotionalPressureLevel, tuple[float, float]] = {
        'Benchmark': (0.0, 0.0),      # 基准需求，无额外增长
        'Low': (0.005, 0.010),        # 低促销压力：0.5% - 1.0%
        'Middle': (0.015, 0.020),     # 中层促销压力：1.5% - 2.0%
        'High': (0.040, 0.055),       # 高促销压力：4.0% - 5.5%
    }
    
    # 产品名称映射（CSV列名 -> 显示名称）
    PRODUCT_NAME_MAP: Dict[str, str] = {
        'demand_orange1L': 'Fressie Orange 1 liter',
        'demand_mango1L': 'Fressie Orange/Mango 1 liter',
        'demand_C1L': 'Fressie Orange/Mango+C 1L',
        'demand_orangePET': 'Fressie Orange PET',
        'demand_cpowerPET': 'Fressie Orange/C-power PET',
        'demand_mangoPET': 'Fressie Orange/Mango PET',
    }
    
    # 反向映射（显示名称 -> CSV列名）
    PRODUCT_NAME_REVERSE_MAP: Dict[str, str] = {v: k for k, v in PRODUCT_NAME_MAP.items()}
    
    # 产品大类映射
    PRODUCT_FAMILIES: Dict[str, str] = {
        'Fressie Orange 1 liter': 'Pack 1L',
        'Fressie Orange/Mango 1 liter': 'Pack 1L',
        'Fressie Orange/Mango+C 1L': 'Pack 1L',
        'Fressie Orange PET': 'PET',
        'Fressie Orange/C-power PET': 'PET',
        'Fressie Orange/Mango PET': 'PET',
    }
    
    def __init__(self, pattern_dir: str = 'demand_history_pattern', 
                 value_dir: str = 'demand_history_value'):
        """
        初始化需求预测引擎
        
        Args:
            pattern_dir: 模式数据目录（包含round_0.csv, round_1.csv等）
            value_dir: 基准值数据目录（包含round_0.csv, round_1.csv等）
        """
        self.pattern_dir = pattern_dir
        self.value_dir = value_dir
        
        # 存储模式数据（按产品）
        self.pattern_data: Dict[str, List[float]] = {}
        
        # 存储基准值数据（按客户-产品）
        self.base_value_data: Dict[str, Dict[str, float]] = {}
        
        # 周模式因子（从pattern数据提取）
        self.weekly_patterns: Dict[str, np.ndarray] = {}
        
        # 随机种子，保证预测可重复
        self.random_state = np.random.RandomState(42)
        
        # 加载数据
        self._load_pattern_data()
        self._load_value_data()
        
        # 分析模式
        self._analyze_patterns()
    
    def _load_pattern_data(self):
        """加载模式数据（用于提取季节性波动）"""
        products = list(self.PRODUCT_NAME_MAP.keys())
        
        # 优先使用round_0（无促销数据）进行模式分析
        pattern_file = os.path.join(self.pattern_dir, 'round_0.csv')
        if os.path.exists(pattern_file):
            with open(pattern_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    for product in products:
                        if product in row:
                            if product not in self.pattern_data:
                                self.pattern_data[product] = []
                            try:
                                self.pattern_data[product].append(float(row[product]))
                            except ValueError:
                                continue
        
        # 如果round_0数据不足，补充round_1数据
        if len(self.pattern_data) == 0:
            pattern_file = os.path.join(self.pattern_dir, 'round_1.csv')
            if os.path.exists(pattern_file):
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        for product in products:
                            if product in row:
                                if product not in self.pattern_data:
                                    self.pattern_data[product] = []
                                try:
                                    self.pattern_data[product].append(float(row[product]))
                                except ValueError:
                                    continue
    
    def _load_value_data(self):
        """加载基准值数据（按客户-产品的基础需求）"""
        # 优先使用round_0（无促销数据）作为基准值
        value_file = os.path.join(self.value_dir, 'round_0.csv')
        if os.path.exists(value_file):
            with open(value_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    customer = row.get('Customer', '')
                    product = row.get('Product', '')
                    demand_str = row.get('Demand per week (units)', '')
                    
                    if customer and product and demand_str:
                        try:
                            demand = float(demand_str)
                            if customer not in self.base_value_data:
                                self.base_value_data[customer] = {}
                            self.base_value_data[customer][product] = demand
                        except ValueError:
                            continue
    
    def _analyze_patterns(self):
        """分析模式数据，提取周波动模式"""
        for product, demands in self.pattern_data.items():
            if len(demands) >= 4:
                demands_array = np.array(demands)
                # 计算周模式（使用全部历史数据的均值归一化）
                mean_demand = demands_array.mean()
                if mean_demand > 0:
                    self.weekly_patterns[product] = demands_array / mean_demand
                else:
                    self.weekly_patterns[product] = np.ones(len(demands))
            else:
                self.weekly_patterns[product] = np.array([1.0, 1.0, 1.0, 1.0])
    
    def _get_pattern_factor(self, product_name: str, week_number: int) -> float:
        """
        获取指定产品在指定周的模式因子
        
        Args:
            product_name: 产品CSV列名（如 'demand_orange1L'）
            week_number: 周数（从1开始）
        
        Returns:
            模式因子（反映季节性波动）
        """
        pattern = self.weekly_patterns.get(product_name, np.ones(4))
        week_index = (week_number - 1) % len(pattern)
        return float(pattern[week_index])
    
    def _calculate_promotional_factor(
        self,
        customer_name: str,
        product_name: str,
        contract: Customer_contract
    ) -> float:
        """
        计算促销压力对需求的影响因子
        
        Args:
            customer_name: 客户名称
            product_name: 产品显示名称
            contract: 客户合同对象
        
        Returns:
            促销影响因子（1.0 + 额外增长百分比）
        """
        # 获取促销压力等级
        promo_pressure = getattr(contract, 'promotional_pressure', 'Benchmark')
        
        # 获取基础增长范围
        base_min, base_max = self.PROMOTIONAL_FACTORS.get(promo_pressure, (0.0, 0.0))
        
        # 随机抽取增长值
        growth = self.random_state.uniform(base_min, base_max)
        
        # 获取客户信息
        customer = next((c for c in CUSTOMERS if c['name'] == customer_name), None)
        
        # Value for Money 客户加倍促销影响
        if customer and customer.get('Value_for_money', False):
            growth *= 2.0
        
        return 1.0 + growth
    
    def predict_weekly_demand(
        self,
        week_number: int,
        customer_contracts: Dict[str, Customer_contract]
    ) -> Dict[str, Dict[str, ProductDemand]]:
        """
        预测指定周各客户-产品的需求量
        
        Args:
            week_number: 要预测的周数（从1开始）
            customer_contracts: 客户合同字典，键为客户名称
        
        Returns:
            嵌套字典，结构: {客户名: {产品名: ProductDemand}}
        """
        results: Dict[str, Dict[str, ProductDemand]] = {}
        
        for customer_name, contract in customer_contracts.items():
            # 获取该客户的基础需求数据
            customer_base_demand = self.base_value_data.get(customer_name, {})
            
            if not customer_base_demand:
                continue
            
            results[customer_name] = {}
            
            for product_display_name, base_demand in customer_base_demand.items():
                # 获取产品CSV列名
                product_csv_name = self.PRODUCT_NAME_REVERSE_MAP.get(product_display_name, '')
                
                # 1. 获取模式因子（季节性波动）
                pattern_factor = self._get_pattern_factor(product_csv_name, week_number)
                
                # 2. 计算促销影响
                promo_factor = self._calculate_promotional_factor(
                    customer_name, product_display_name, contract
                )
                
                # 3. 计算最终需求（加入小幅度随机波动）
                base_with_pattern = base_demand * pattern_factor
                promo_adjusted = base_with_pattern * promo_factor
                
                # 添加5%以内的随机波动
                random_noise = self.random_state.normal(1.0, 0.05)
                final_demand = max(0.0, promo_adjusted * random_noise)
                
                results[customer_name][product_display_name] = {
                    'product_name': product_display_name,
                    'customer_name': customer_name,
                    'base_demand': base_demand,
                    'pattern_factor': pattern_factor,
                    'promotional_factor': promo_factor,
                    'final_demand': final_demand
                }
        
        return results
    
    def predict_period_demand(
        self,
        start_week: int,
        num_weeks: int,
        customer_contracts: Dict[str, Customer_contract]
    ) -> Dict[int, Dict[str, Dict[str, ProductDemand]]]:
        """
        预测多个连续周的需求量
        
        Args:
            start_week: 起始周数
            num_weeks: 预测周数
            customer_contracts: 客户合同字典
        
        Returns:
            每周的预测需求，键为周数
        """
        period_results = {}
        
        for week in range(start_week, start_week + num_weeks):
            period_results[week] = self.predict_weekly_demand(week, customer_contracts)
        
        return period_results
    
    def get_total_demand_by_customer(
        self,
        week_number: int,
        customer_contracts: Dict[str, Customer_contract]
    ) -> Dict[str, float]:
        """
        获取指定周各客户的总需求量
        
        Args:
            week_number: 周数
            customer_contracts: 客户合同字典
        
        Returns:
            各客户的总需求量
        """
        weekly_demand = self.predict_weekly_demand(week_number, customer_contracts)
        totals = {}
        
        for customer_name, products in weekly_demand.items():
            totals[customer_name] = sum(p['final_demand'] for p in products.values())
        
        return totals
    
    def get_total_demand_by_product(
        self,
        week_number: int,
        customer_contracts: Dict[str, Customer_contract]
    ) -> Dict[str, float]:
        """
        获取指定周各产品的总需求量（跨所有客户）
        
        Args:
            week_number: 周数
            customer_contracts: 客户合同字典
        
        Returns:
            各产品的总需求量
        """
        weekly_demand = self.predict_weekly_demand(week_number, customer_contracts)
        totals = {}
        
        for customer_name, products in weekly_demand.items():
            for product_name, demand_data in products.items():
                if product_name not in totals:
                    totals[product_name] = 0.0
                totals[product_name] += demand_data['final_demand']
        
        return totals
    
    def get_total_demand_by_family(
        self,
        week_number: int,
        customer_contracts: Dict[str, Customer_contract],
        family_type: str = None
    ) -> Dict[str, float]:
        """
        获取指定产品大类的总需求
        
        Args:
            week_number: 周数
            customer_contracts: 客户合同字典
            family_type: 产品大类 ('PET', 'Pack 1L')，None表示全部
        
        Returns:
            各产品大类的总需求量
        """
        weekly_demand = self.predict_weekly_demand(week_number, customer_contracts)
        totals = {}
        
        for customer_name, products in weekly_demand.items():
            for product_name, demand_data in products.items():
                family = self.PRODUCT_FAMILIES.get(product_name, 'Other')
                
                if family_type is not None and family != family_type:
                    continue
                
                if family not in totals:
                    totals[family] = 0.0
                totals[family] += demand_data['final_demand']
        
        return totals
    
    def get_overall_total_demand(
        self,
        week_number: int,
        customer_contracts: Dict[str, Customer_contract]
    ) -> float:
        """
        获取指定周的总需求量（所有客户所有产品）
        
        Args:
            week_number: 周数
            customer_contracts: 客户合同字典
        
        Returns:
            总需求量
        """
        weekly_demand = self.predict_weekly_demand(week_number, customer_contracts)
        total = 0.0
        
        for customer_name, products in weekly_demand.items():
            total += sum(p['final_demand'] for p in products.values())
        
        return total


# 全局预测引擎实例
_global_forecast_engine = None


def get_forecast_engine() -> DemandForecastEngine:
    """
    获取全局需求预测引擎实例（单例模式）
    
    Returns:
        DemandForecastEngine 实例
    """
    global _global_forecast_engine
    if _global_forecast_engine is None:
        _global_forecast_engine = DemandForecastEngine(
            pattern_dir='demand_history_pattern',
            value_dir='demand_history_value'
        )
    return _global_forecast_engine