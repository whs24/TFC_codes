#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time: 2026/5/22
# @Author: Demand Forecast Visualization Script

import os
import matplotlib.pyplot as plt
from demand_forecast import DemandForecastEngine
from sales import Customer_contract


def main():
    """
    Run demand forecast and generate visualization charts
    
    Forecast 26 weeks of demand and output individual charts for each product
    """
    # Initialize forecast engine
    engine = DemandForecastEngine(
        pattern_dir='demand_history_pattern',
        value_dir='demand_history_value'
    )
    
    # Create sample contract data with different promotional pressure levels
    sample_contracts = {
        'Super': Customer_contract(
            supplier_name='TFC',
            contract_index=1.0,
            service_level=95.0,
            shelf_life=21,
            order_deadline=2,
            trade_unit='Pallet',
            payment_term=30,
            promotional_pressure='Middle',
            promotion_horizon=4,
            vmi_supplier=False
        ),
        'Convi': Customer_contract(
            supplier_name='TFC',
            contract_index=0.95,
            service_level=90.0,
            shelf_life=14,
            order_deadline=1,
            trade_unit='Case',
            payment_term=15,
            promotional_pressure='High',
            promotion_horizon=2,
            vmi_supplier=True
        ),
        'SAVE': Customer_contract(
            supplier_name='TFC',
            contract_index=0.98,
            service_level=92.0,
            shelf_life=18,
            order_deadline=2,
            trade_unit='Pallet',
            payment_term=45,
            promotional_pressure='Low',
            promotion_horizon=3,
            vmi_supplier=False
        ),
    }
    
    # Forecast 26 weeks
    num_weeks = 26
    start_week = 1
    
    print(f"Forecasting demand for weeks {start_week} - {start_week + num_weeks - 1}...")
    
    # Get weekly demand per product
    weekly_product_demand = {}  # {week: {product: demand}}
    
    for week in range(start_week, start_week + num_weeks):
        product_totals = engine.get_total_demand_by_product(week, sample_contracts)
        weekly_product_demand[week] = product_totals
    
    # Extract all products
    all_products = set()
    for week, products in weekly_product_demand.items():
        all_products.update(products.keys())
    
    # Create output directories
    os.makedirs('forecast_charts', exist_ok=True)
    os.makedirs('forecast_charts/individual', exist_ok=True)  # For individual product charts
    
    # 1. Create subplot grid (2 rows x 3 columns) with individual Y axes
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(18, 10))
    axes = axes.flatten()  # Flatten to 1D array
    
    sorted_products = sorted(all_products)
    
    for i, product in enumerate(sorted_products):
        ax = axes[i]
        weeks = sorted(weekly_product_demand.keys())
        demands = [weekly_product_demand[week].get(product, 0) for week in weeks]
        
        ax.plot(weeks, demands, marker='o', markersize=4, color=f'C{i}')
        ax.set_title(product, fontsize=10)
        ax.set_xlabel('Week', fontsize=8)
        ax.set_ylabel('Demand (units)', fontsize=8)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.tick_params(axis='both', labelsize=7)
        
        # Set y-axis to auto-scale for each subplot
        ax.autoscale(True, axis='y')
    
    # Adjust layout
    plt.tight_layout()
    plt.savefig('forecast_charts/all_products_subplots.png', dpi=150)
    plt.close()
    
    print("Generated: forecast_charts/all_products_subplots.png")
    
    # 2. Create individual chart for each product
    for i, product in enumerate(sorted_products):
        plt.figure(figsize=(10, 5))
        weeks = sorted(weekly_product_demand.keys())
        demands = [weekly_product_demand[week].get(product, 0) for week in weeks]
        
        plt.plot(weeks, demands, marker='o', markersize=4, color=f'C{i}')
        plt.title(f'{product} - 26-Week Demand Forecast', fontsize=12)
        plt.xlabel('Week', fontsize=10)
        plt.ylabel('Demand (units)', fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save individual chart
        filename = f'forecast_charts/individual/{product.replace("/", "_").replace(" ", "_")}.png'
        plt.savefig(filename, dpi=150)
        plt.close()
        
        print(f"Generated: {filename}")
    
    # 3. Original combined chart (for reference)
    plt.figure(figsize=(14, 8))
    
    for i, product in enumerate(sorted(all_products)):
        weeks = sorted(weekly_product_demand.keys())
        demands = [weekly_product_demand[week].get(product, 0) for week in weeks]
        
        plt.plot(weeks, demands, marker='o', markersize=4, label=product)
    
    plt.title('26-Week Product Demand Forecast (Combined)', fontsize=14)
    plt.xlabel('Week', fontsize=12)
    plt.ylabel('Demand (units)', fontsize=12)
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1), fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('forecast_charts/all_products_combined.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Generated: forecast_charts/all_products_combined.png")
    
    # 4. By product family (shared Y-axis within family)
    product_families = {
        'Pack 1L': [
            'Fressie Orange 1 liter',
            'Fressie Orange/Mango 1 liter',
            'Fressie Orange/Mango+C 1L'
        ],
        'PET': [
            'Fressie Orange PET',
            'Fressie Orange/C-power PET',
            'Fressie Orange/Mango PET'
        ]
    }
    
    for family, products in product_families.items():
        plt.figure(figsize=(12, 6))
        
        for i, product in enumerate(products):
            if product not in all_products:
                continue
            weeks = sorted(weekly_product_demand.keys())
            demands = [weekly_product_demand[week].get(product, 0) for week in weeks]
            
            plt.plot(weeks, demands, marker='o', markersize=4, label=product)
        
        plt.title(f'{family} Products 26-Week Demand Forecast', fontsize=14)
        plt.xlabel('Week', fontsize=12)
        plt.ylabel('Demand (units)', fontsize=12)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f'forecast_charts/{family}_26weeks.png', dpi=150)
        plt.close()
        
        print(f"Generated: forecast_charts/{family}_26weeks.png")
    
    # 5. Customer totals
    plt.figure(figsize=(12, 6))
    
    for customer in sample_contracts.keys():
        weekly_totals = []
        for week in range(start_week, start_week + num_weeks):
            customer_totals = engine.get_total_demand_by_customer(week, sample_contracts)
            weekly_totals.append(customer_totals.get(customer, 0))
        
        plt.plot(range(start_week, start_week + num_weeks), weekly_totals, 
                 marker='o', markersize=4, label=customer)
    
    plt.title('26-Week Total Demand by Customer', fontsize=14)
    plt.xlabel('Week', fontsize=12)
    plt.ylabel('Demand (units)', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('forecast_charts/customer_totals_26weeks.png', dpi=150)
    plt.close()
    
    print("Generated: forecast_charts/customer_totals_26weeks.png")
    
    # 6. Output statistics summary
    print("\n" + "=" * 60)
    print("Forecast Statistics Summary")
    print("=" * 60)
    
    for product in sorted(all_products):
        demands = []
        for week in range(start_week, start_week + num_weeks):
            demands.append(weekly_product_demand[week].get(product, 0))
        
        avg_demand = sum(demands) / len(demands)
        min_demand = min(demands)
        max_demand = max(demands)
        volatility = (max_demand - min_demand) / avg_demand * 100 if avg_demand > 0 else 0
        
        print(f"\n{product}:")
        print(f"  Average: {avg_demand:.0f} units")
        print(f"  Minimum: {min_demand:.0f} units")
        print(f"  Maximum: {max_demand:.0f} units")
        print(f"  Volatility: {volatility:.1f}%")
    
    print("\nTotal Demand per Week:")
    for week in range(start_week, start_week + num_weeks):
        total = engine.get_overall_total_demand(week, sample_contracts)
        print(f"  Week {week}: {total:.0f} units")
    
    print("\n" + "=" * 60)
    print("Charts saved to forecast_charts/ directory")
    print("=" * 60)


if __name__ == '__main__':
    main()