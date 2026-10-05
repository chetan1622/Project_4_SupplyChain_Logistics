# =============================================================================
# PROJECT  : Supply Chain & Logistics Analytics
# SCRIPT   : 03_analytics_engine.py
# AUTHOR   : Chetan
# DESC     : 5 core analytics modules:
#            1. Vendor Scorecard  2. Demand-Supply Gap
#            3. Freight Cost Optimization  4. Inventory Turnover
#            5. Regional Performance Analysis
# =============================================================================

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
REPORTS_DIR   = os.path.join(BASE_DIR, 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

report_lines = []

def rprint(line=""):
    print(line)
    report_lines.append(line)

def section(title):
    rprint()
    rprint("=" * 65)
    rprint(f"  {title}")
    rprint("=" * 65)


# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────
def load_all():
    rprint("Loading cleaned data...")
    orders     = pd.read_csv(os.path.join(PROCESSED_DIR, 'cleaned_orders.csv'), parse_dates=['order_date'])
    suppliers  = pd.read_csv(os.path.join(PROCESSED_DIR, 'cleaned_suppliers.csv'))
    products   = pd.read_csv(os.path.join(PROCESSED_DIR, 'cleaned_products.csv'))
    warehouses = pd.read_csv(os.path.join(PROCESSED_DIR, 'cleaned_warehouses.csv'))
    inventory  = pd.read_csv(os.path.join(PROCESSED_DIR, 'cleaned_inventory.csv'))
    rprint(f"  Orders: {len(orders):,} | Suppliers: {len(suppliers):,} | Products: {len(products):,}")
    return orders, suppliers, products, warehouses, inventory


# ─────────────────────────────────────────────────────────────
# ANALYSIS 1 : VENDOR SCORECARD
# ─────────────────────────────────────────────────────────────
def vendor_scorecard(orders, suppliers):
    section("ANALYSIS 1 — VENDOR SCORECARD")

    # Aggregate order-level metrics per supplier
    sup_orders = orders.groupby('supplier_id').agg(
        total_orders    = ('order_id', 'count'),
        avg_delay_days  = ('delay_days', 'mean'),
        on_time_count   = ('delivery_status', lambda x: (x == 'On-Time').sum()),
        total_value_inr = ('total_cost_inr', 'sum'),
        avg_fulfillment = ('fulfillment_rate', 'mean'),
    ).reset_index()

    sup_orders['order_on_time_rate'] = (sup_orders['on_time_count'] / sup_orders['total_orders'] * 100).round(2)

    # Merge supplier master data
    merged = sup_orders.merge(
        suppliers[['supplier_id', 'supplier_name', 'quality_rating', 'on_time_delivery_rate', 'region']],
        on='supplier_id', how='left'
    )

    max_delay = merged['avg_delay_days'].max()
    # Composite score: 40% OTD, 30% quality, 30% delay penalty
    merged['vendor_score'] = (
        merged['on_time_delivery_rate'] * 0.40 +
        (merged['quality_rating'] / 5 * 100) * 0.30 +
        (1 - merged['avg_delay_days'].clip(0) / max(max_delay, 1)) * 100 * 0.30
    ).round(2)

    merged['vendor_rank'] = merged['vendor_score'].rank(ascending=False).astype(int)
    merged['vendor_tier'] = merged['vendor_score'].apply(
        lambda s: 'Preferred' if s >= 80 else ('Standard' if s >= 65 else 'At-Risk'))

    rprint("\n  TOP 10 VENDORS BY SCORE:")
    rprint(merged.nlargest(10, 'vendor_score')[
        ['supplier_name', 'vendor_score', 'vendor_tier', 'on_time_delivery_rate',
         'quality_rating', 'total_orders']].to_string(index=False))

    rprint("\n  BOTTOM 10 VENDORS (At-Risk):")
    rprint(merged.nsmallest(10, 'vendor_score')[
        ['supplier_name', 'vendor_score', 'vendor_tier', 'avg_delay_days', 'total_orders']].to_string(index=False))

    tier_counts = merged['vendor_tier'].value_counts()
    rprint(f"\n  VENDOR TIER DISTRIBUTION:\n  {tier_counts.to_string()}")
    return merged


# ─────────────────────────────────────────────────────────────
# ANALYSIS 2 : DEMAND-SUPPLY GAP
# ─────────────────────────────────────────────────────────────
def demand_supply_gap(orders, products):
    section("ANALYSIS 2 — DEMAND-SUPPLY GAP ANALYSIS")

    prod_summary = orders.groupby('product_id').agg(
        total_ordered  = ('quantity_ordered', 'sum'),
        total_received = ('quantity_received', 'sum'),
        order_count    = ('order_id', 'count'),
    ).reset_index()

    prod_summary['fulfillment_rate'] = (prod_summary['total_received'] / prod_summary['total_ordered'] * 100).round(2)
    prod_summary['supply_gap_units'] = prod_summary['total_ordered'] - prod_summary['total_received']
    prod_summary['risk_flag']        = prod_summary['fulfillment_rate'].apply(
        lambda x: 'HIGH RISK' if x < 80 else ('MEDIUM RISK' if x < 90 else 'LOW RISK'))

    merged = prod_summary.merge(products[['product_id', 'product_name', 'category']], on='product_id', how='left')

    rprint("\n  TOP 20 HIGH-RISK SKUs (Fulfillment < 90%):")
    risky = merged[merged['risk_flag'].isin(['HIGH RISK', 'MEDIUM RISK'])].nsmallest(20, 'fulfillment_rate')
    rprint(risky[['product_name', 'category', 'fulfillment_rate', 'supply_gap_units', 'risk_flag']].to_string(index=False))

    rprint(f"\n  Total HIGH RISK SKUs  : {(merged['risk_flag']=='HIGH RISK').sum()}")
    rprint(f"  Total MEDIUM RISK SKUs: {(merged['risk_flag']=='MEDIUM RISK').sum()}")
    rprint(f"  Total LOW RISK SKUs   : {(merged['risk_flag']=='LOW RISK').sum()}")
    return merged


# ─────────────────────────────────────────────────────────────
# ANALYSIS 3 : FREIGHT COST OPTIMIZATION
# ─────────────────────────────────────────────────────────────
def freight_optimization(orders):
    section("ANALYSIS 3 — FREIGHT COST OPTIMIZATION")

    mode_summary = orders.groupby('freight_mode').agg(
        order_count     = ('order_id', 'count'),
        total_freight   = ('freight_cost_inr', 'sum'),
        avg_cost_per_kg = ('freight_cost_per_kg', 'mean'),
        total_weight_kg = ('freight_cost_inr', 'count'),  # proxy
    ).reset_index()

    mode_summary['share_pct'] = (mode_summary['total_freight'] / mode_summary['total_freight'].sum() * 100).round(2)
    rprint("\n  FREIGHT COST BY MODE:")
    rprint(mode_summary.to_string(index=False))

    # Calculate savings: switch Air -> Road for shipments <= 500kg
    air_orders  = orders[orders['freight_mode'] == 'Air'].copy()
    road_avg_kg = orders[orders['freight_mode'] == 'Road']['freight_cost_per_kg'].mean()

    air_orders['potential_road_cost'] = air_orders['freight_cost_inr'] / \
                                         air_orders['freight_cost_per_kg'] * road_avg_kg
    air_orders['savings_inr']         = air_orders['freight_cost_inr'] - air_orders['potential_road_cost']
    potential_savings = air_orders['savings_inr'].sum()

    rprint(f"\n  Air shipment orders        : {len(air_orders):,}")
    rprint(f"  Avg Air cost/kg            : ₹{air_orders['freight_cost_per_kg'].mean():.2f}")
    rprint(f"  Avg Road cost/kg           : ₹{road_avg_kg:.2f}")
    rprint(f"  POTENTIAL ANNUAL SAVINGS   : ₹{potential_savings:,.0f}")
    rprint(f"  (Switching 30% Air → Road  : ₹{potential_savings * 0.30:,.0f} savings)")
    return mode_summary


# ─────────────────────────────────────────────────────────────
# ANALYSIS 4 : INVENTORY TURNOVER & DEAD STOCK
# ─────────────────────────────────────────────────────────────
def inventory_turnover(inventory, products):
    section("ANALYSIS 4 — INVENTORY TURNOVER & DEAD STOCK")

    prod_inv = inventory.groupby('product_id').agg(
        total_dispatched = ('dispatched_qty', 'sum'),
        avg_closing_stock= ('closing_stock', 'mean'),
        stockout_events  = ('stockout_flag', 'sum'),
        avg_doi          = ('days_of_inventory', 'mean'),
    ).reset_index()

    prod_inv['inventory_turnover'] = (
        prod_inv['total_dispatched'] / prod_inv['avg_closing_stock'].replace(0, np.nan)
    ).fillna(0).round(2)

    prod_inv['stock_status'] = prod_inv['inventory_turnover'].apply(
        lambda t: 'Dead Stock' if t < 2 else ('Slow Moving' if t < 6 else 'Fast Moving'))

    merged = prod_inv.merge(products[['product_id', 'product_name', 'category', 'unit_price_inr']], on='product_id', how='left')
    merged['holding_cost_inr'] = (merged['avg_closing_stock'] * merged['unit_price_inr'] * 0.20).round(2)  # 20% holding cost

    dead_stock = merged[merged['stock_status'] == 'Dead Stock'].sort_values('holding_cost_inr', ascending=False)
    rprint(f"\n  DEAD STOCK PRODUCTS (Turnover < 2x): {len(dead_stock)}")
    rprint(dead_stock[['product_name', 'category', 'inventory_turnover',
                         'avg_closing_stock', 'holding_cost_inr']].head(15).to_string(index=False))

    total_dead_cost = dead_stock['holding_cost_inr'].sum()
    rprint(f"\n  Total Annual Dead Stock Holding Cost : ₹{total_dead_cost:,.0f}")
    return merged


# ─────────────────────────────────────────────────────────────
# ANALYSIS 5 : REGIONAL PERFORMANCE
# ─────────────────────────────────────────────────────────────
def regional_performance(orders, warehouses):
    section("ANALYSIS 5 — REGIONAL PERFORMANCE ANALYSIS")

    merged = orders.merge(warehouses[['warehouse_id', 'region']], on='warehouse_id', how='left')

    regional = merged.groupby('region').agg(
        total_orders        = ('order_id', 'count'),
        on_time_orders      = ('delivery_status', lambda x: (x == 'On-Time').sum()),
        avg_delay_days      = ('delay_days', 'mean'),
        total_freight_inr   = ('freight_cost_inr', 'sum'),
        avg_fulfillment     = ('fulfillment_rate', 'mean'),
        total_order_value   = ('total_cost_inr', 'sum'),
    ).reset_index()

    regional['fulfillment_rate_pct'] = (regional['on_time_orders'] / regional['total_orders'] * 100).round(2)
    regional['freight_pct_of_value'] = (regional['total_freight_inr'] / regional['total_order_value'] * 100).round(2)

    rprint("\n  REGIONAL PERFORMANCE SUMMARY:")
    rprint(regional[['region', 'total_orders', 'fulfillment_rate_pct',
                      'avg_delay_days', 'total_freight_inr', 'freight_pct_of_value']].to_string(index=False))
    return regional


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    rprint("=" * 65)
    rprint("  SUPPLY CHAIN & LOGISTICS — ANALYTICS ENGINE")
    rprint("=" * 65)

    orders, suppliers, products, warehouses, inventory = load_all()

    vendor_df   = vendor_scorecard(orders, suppliers)
    gap_df      = demand_supply_gap(orders, products)
    freight_df  = freight_optimization(orders)
    inv_df      = inventory_turnover(inventory, products)
    regional_df = regional_performance(orders, warehouses)

    # Save report
    report_path = os.path.join(REPORTS_DIR, 'analytics_summary.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print(f"\n✓ Analytics complete! Summary saved to {report_path}")
