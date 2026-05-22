# --- Finance ---

roi = 0  # = operating_profit / investment

# --- 财报补充科目 ---
contract_costs = 0
investment_software = 0
investment_building = 0

# --- KPI / 结果指标（待填）---
rejection_rate_components = 0
distributed_pallets = 0
availability_for_production = 0
utilization_rate_bottling_lines = 0
utilization_rate_tank_yard = 0
capacity_loss_due_to_changeovers = 0
capacity_loss_due_to_breakdowns = 0
delivery_reliability = 0
on_shelf_availability = 0
economic_inventory = 0
days_payable_outstanding = 0
cash_to_cash_cycle = 0
overall_equipment_effectiveness = 0
carbon_footprint = 0
co2_emission = 0

realized_revenue = 0 # = contracted_sales_revenue + bonus_or_penalties
contracted_sales_revenue = 0 # sum over all customers
bonus_or_penalties = 0 # = service_level (temporarily)
bonus_or_penalties_service_level = 0 # sum over all customers

gross_margin = 0 # = realized_revenue - cost_of_goods_sold
cost_of_goods_sold = 0 # = purchase_value + production_costs
purchase_value = 0 # sum over all suppliers
production_costs = 0 # = bottling_lines_fixed_costs + permanent_employees + flexible_manpower + outsourcing + mixer_fixed_costs + mixer_variable_costs
production_costs_bottling_lines_fixed_costs = 0
production_costs_permanent_employees = 0
production_costs_flexible_manpower = 0
production_costs_outsourcing = 0
production_costs_mixer_fixed_costs = 0
production_costs_mixer_variable_costs = 0

indirect_cost = 0 # = overhead_costs + stock_costs + handling_costs + administration_costs + distribution_costs + project_costs + interest
overhead_costs = 0 # = energy + water + other
overhead_costs_energy = 0
overhead_costs_water = 0
overhead_costs_other = 0
stock_costs = 0 # = interest_on_stock_value + space + risk
interest_on_stock_value = 0 # = interest_components + interest_products
interest_on_stock_value_interest_components = 0
interest_on_stock_value_interest_products = 0
space = 0 # = pallet_locations_raw_materials_warehouse + outsourcing_tank_yard + pallet_locations_finished_goods_warehouse + overflow_finished_goods_warehouse
space_pallet_locations_raw_materials_warehouse = 0
space_outsourcing_tank_yard = 0
space_pallet_locations_finished_goods_warehouse = 0
space_overflow_finished_goods_warehouse = 0
risk = 0 # = costs_of_scrap
risk_costs_of_scrap = 0
handling_costs = 0 # = inbound_handling + outbound_handling
inbound_handling = 0 # = inbound_permanent_employees + raw_materials_inspection
inbound_handling_inbound_permanent_employees = 0
inbound_handling_raw_materials_inspection = 0
outbound_handling = 0 # = outbound_permanent_employees + outbound_flexible_manpower
outbound_handling_outbound_permanent_employees = 0
outbound_handling_outbound_flexible_manpower = 0
administration_costs = 0 # = inbound + outbound
inbound = 0 # = inbound_order_lines + inbound_orders + contracted_suppliers
inbound_inbound_order_lines = 0
inbound_inbound_orders = 0
inbound_contracted_suppliers = 0
outbound = 0 # = outbound_order_lines + outbound_orders
outbound_outbound_order_lines = 0
outbound_outbound_orders = 0
distribution_costs = 0
project_costs = 0 # including SMED, inflate PET bottles, etc.
interest = 0

operating_profit = 0 # = gross_margin - indirect_cost

investment = 0 # = fixed + stock + machines + payment_terms
investment_fixed = 0
investment_stock = 0
investment_machines = 0
investment_payment_terms = 0