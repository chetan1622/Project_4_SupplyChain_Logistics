# =============================================================================
# PROJECT  : Supply Chain & Logistics Analytics
# SCRIPT   : 01_data_generation.py
# AUTHOR   : Chetan
# DESC     : Generates 60,000+ realistic supply chain records
#            5 tables: products, suppliers, warehouses, orders, inventory
# =============================================================================

import pandas as pd
import numpy as np
from faker import Faker
import random
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

fake = Faker('en_IN')
np.random.seed(42)
random.seed(42)

# Output directory
RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'raw')
os.makedirs(RAW_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# MASTER DATA
# ─────────────────────────────────────────────────────────────
INDIAN_CITIES = [
    ('Mumbai', 'Maharashtra', 'West'),
    ('Delhi', 'Delhi', 'North'),
    ('Bengaluru', 'Karnataka', 'South'),
    ('Chennai', 'Tamil Nadu', 'South'),
    ('Hyderabad', 'Telangana', 'South'),
    ('Pune', 'Maharashtra', 'West'),
    ('Ahmedabad', 'Gujarat', 'West'),
    ('Kolkata', 'West Bengal', 'East'),
    ('Jaipur', 'Rajasthan', 'North'),
    ('Lucknow', 'Uttar Pradesh', 'North'),
    ('Surat', 'Gujarat', 'West'),
    ('Nagpur', 'Maharashtra', 'Central'),
    ('Bhopal', 'Madhya Pradesh', 'Central'),
    ('Patna', 'Bihar', 'East'),
    ('Kochi', 'Kerala', 'South'),
]

CATEGORIES = {
    'Electronics':   ['Smartphones', 'Laptops', 'Tablets', 'Headphones', 'Cameras'],
    'FMCG':          ['Packaged Food', 'Beverages', 'Personal Care', 'Household', 'Dairy'],
    'Pharma':        ['OTC Medicines', 'Prescription Drugs', 'Surgical Supplies', 'Vitamins'],
    'Apparel':       ['Mens Wear', 'Womens Wear', 'Kids Wear', 'Sportswear', 'Footwear'],
    'Auto Parts':    ['Engine Parts', 'Tyres', 'Batteries', 'Filters', 'Brakes'],
}

FREIGHT_MODES = ['Road', 'Rail', 'Air', 'Sea']
FREIGHT_COST_PER_KG = {'Road': (8, 18), 'Rail': (4, 10), 'Air': (60, 120), 'Sea': (2, 6)}


# ─────────────────────────────────────────────────────────────
# TABLE 1 : PRODUCTS (500 rows)
# ─────────────────────────────────────────────────────────────
def generate_products(n=500):
    print(f"Generating {n} products...")
    rows = []
    for i in range(1, n + 1):
        cat = random.choice(list(CATEGORIES.keys()))
        subcat = random.choice(CATEGORIES[cat])
        price = round(random.uniform(50, 50000), 2)
        weight = round(random.uniform(0.1, 50), 2)
        volume = round(weight * random.uniform(0.001, 0.005), 4)
        rows.append({
            'product_id':    f'PRD-{i:04d}',
            'product_name':  f'{subcat} {fake.word().title()} {random.choice(["Pro", "Lite", "Plus", "Max", ""])}',
            'category':      cat,
            'subcategory':   subcat,
            'sku':           f'SKU-{cat[:3].upper()}-{i:05d}',
            'unit_price_inr': price,
            'weight_kg':     weight,
            'volume_cbm':    volume,
            'reorder_point': random.randint(10, 200),
            'lead_time_days': random.randint(2, 30),
        })
    df = pd.DataFrame(rows)
    path = os.path.join(RAW_DIR, 'products.csv')
    df.to_csv(path, index=False)
    print(f"  ✓ products.csv saved — Shape: {df.shape}")
    print(df.head(3).to_string())
    return df


# ─────────────────────────────────────────────────────────────
# TABLE 2 : SUPPLIERS (200 rows)
# ─────────────────────────────────────────────────────────────
def generate_suppliers(n=200):
    print(f"\nGenerating {n} suppliers...")
    state_codes = {'Maharashtra': '27', 'Delhi': '07', 'Karnataka': '29',
                   'Tamil Nadu': '33', 'Telangana': '36', 'Gujarat': '24',
                   'West Bengal': '19', 'Rajasthan': '08', 'Uttar Pradesh': '09',
                   'Madhya Pradesh': '23', 'Kerala': '32', 'Bihar': '10'}
    
    company_suffixes = ['Industries Ltd', 'Enterprises Pvt Ltd', 'Trading Co', 'Logistics Pvt Ltd',
                        'Distributors', 'Supply Chain Pvt Ltd', 'Warehousing Ltd', 'Exports Ltd']
    rows = []
    for i in range(1, n + 1):
        city, state, region = random.choice(INDIAN_CITIES)
        sc = state_codes.get(state, '27')
        pan_like  = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5)) + \
                    ''.join(random.choices('0123456789', k=4)) + \
                    random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        gstin = f"{sc}{pan_like}1Z{random.randint(1,9)}"
        on_time = round(random.uniform(60, 99), 1)
        rows.append({
            'supplier_id':           f'SUP-{i:03d}',
            'supplier_name':         fake.company() + ' ' + random.choice(company_suffixes),
            'city':                  city,
            'state':                 state,
            'region':                region,
            'gstin':                 gstin,
            'contact_email':         fake.email(),
            'payment_terms_days':    random.choice([15, 30, 45, 60, 90]),
            'quality_rating':        round(random.uniform(2.0, 5.0), 1),
            'on_time_delivery_rate': on_time,
        })
    df = pd.DataFrame(rows)
    path = os.path.join(RAW_DIR, 'suppliers.csv')
    df.to_csv(path, index=False)
    print(f"  ✓ suppliers.csv saved — Shape: {df.shape}")
    print(df.head(3).to_string())
    return df


# ─────────────────────────────────────────────────────────────
# TABLE 3 : WAREHOUSES (20 rows)
# ─────────────────────────────────────────────────────────────
def generate_warehouses(n=20):
    print(f"\nGenerating {n} warehouses...")
    rows = []
    for i in range(1, n + 1):
        city, state, region = INDIAN_CITIES[i % len(INDIAN_CITIES)]
        capacity = random.randint(5000, 50000)
        utilization = round(random.uniform(45, 95), 1)
        rows.append({
            'warehouse_id':          f'WH-{i:02d}',
            'warehouse_name':        f'{city} {random.choice(["Central", "North", "South", "East"])} Warehouse',
            'city':                  city,
            'state':                 state,
            'region':                region,
            'capacity_units':        capacity,
            'current_utilization_pct': utilization,
            'monthly_cost_inr':      random.randint(200000, 2000000),
        })
    df = pd.DataFrame(rows)
    path = os.path.join(RAW_DIR, 'warehouses.csv')
    df.to_csv(path, index=False)
    print(f"  ✓ warehouses.csv saved — Shape: {df.shape}")
    print(df.head(3).to_string())
    return df


# ─────────────────────────────────────────────────────────────
# TABLE 4 : ORDERS (50,000 rows)
# ─────────────────────────────────────────────────────────────
def generate_orders(products_df, suppliers_df, warehouses_df, n=50000):
    print(f"\nGenerating {n} orders...")
    start_date = datetime(2023, 1, 1)
    end_date   = datetime(2024, 9, 30)
    date_range = (end_date - start_date).days

    product_ids   = products_df['product_id'].tolist()
    supplier_ids  = suppliers_df['supplier_id'].tolist()
    warehouse_ids = warehouses_df['warehouse_id'].tolist()
    
    # Build lookup dicts
    prod_lookup = products_df.set_index('product_id')[['unit_price_inr', 'weight_kg', 'lead_time_days']].to_dict('index')
    sup_lookup  = suppliers_df.set_index('supplier_id')['on_time_delivery_rate'].to_dict()

    rows = []
    for i in range(1, n + 1):
        order_date = start_date + timedelta(days=random.randint(0, date_range))
        prod_id    = random.choice(product_ids)
        sup_id     = random.choice(supplier_ids)
        wh_id      = random.choice(warehouse_ids)
        
        prod = prod_lookup[prod_id]
        qty  = random.randint(1, 500)
        unit_cost = prod['unit_price_inr'] * random.uniform(0.6, 0.85)  # wholesale discount
        total_cost = round(qty * unit_cost, 2)
        
        lead_days = prod['lead_time_days'] + random.randint(-2, 5)
        expected_delivery = order_date + timedelta(days=max(1, lead_days))
        
        # Simulate delay based on supplier on-time rate
        otr = sup_lookup[sup_id] / 100
        if random.random() < otr:
            delay_days = random.choice([0, 0, 0, -1, -2])  # on time or early
        else:
            delay_days = random.randint(1, 15)
        
        actual_delivery = expected_delivery + timedelta(days=delay_days)
        
        if delay_days <= 0:
            status = 'On-Time' if delay_days == 0 else 'Early'
        elif delay_days <= 3:
            status = 'Slightly Late'
        else:
            status = 'Very Late'
        
        mode = random.choices(FREIGHT_MODES, weights=[60, 20, 10, 10])[0]
        wt = prod['weight_kg'] * qty
        lo, hi = FREIGHT_COST_PER_KG[mode]
        freight_per_kg = round(random.uniform(lo, hi), 2)
        freight_cost   = round(wt * freight_per_kg, 2)
        
        qty_recv = qty if random.random() > 0.05 else int(qty * random.uniform(0.85, 0.99))
        
        rows.append({
            'order_id':              f'ORD-{i:06d}',
            'order_date':            order_date.strftime('%Y-%m-%d'),
            'product_id':            prod_id,
            'supplier_id':           sup_id,
            'warehouse_id':          wh_id,
            'quantity_ordered':      qty,
            'quantity_received':     qty_recv,
            'unit_cost_inr':         round(unit_cost, 2),
            'total_cost_inr':        total_cost,
            'expected_delivery_date': expected_delivery.strftime('%Y-%m-%d'),
            'actual_delivery_date':  actual_delivery.strftime('%Y-%m-%d'),
            'delivery_status':       status,
            'delay_days':            delay_days,
            'freight_mode':          mode,
            'freight_cost_inr':      freight_cost,
            'freight_cost_per_kg':   freight_per_kg,
        })

    df = pd.DataFrame(rows)
    path = os.path.join(RAW_DIR, 'orders.csv')
    df.to_csv(path, index=False)
    print(f"  ✓ orders.csv saved — Shape: {df.shape}")
    print(df.head(3).to_string())
    return df


# ─────────────────────────────────────────────────────────────
# TABLE 5 : INVENTORY (10,000 snapshots)
# ─────────────────────────────────────────────────────────────
def generate_inventory(products_df, warehouses_df, n=10000):
    print(f"\nGenerating {n} inventory snapshots...")
    start_date    = datetime(2023, 1, 1)
    product_ids   = products_df['product_id'].tolist()
    warehouse_ids = warehouses_df['warehouse_id'].tolist()
    
    rows = []
    for i in range(1, n + 1):
        snap_date    = start_date + timedelta(days=random.randint(0, 639))
        prod_id      = random.choice(product_ids)
        wh_id        = random.choice(warehouse_ids)
        opening      = random.randint(0, 2000)
        received     = random.randint(0, 500)
        dispatched   = random.randint(0, min(opening + received, 600))
        closing      = opening + received - dispatched
        stockout     = 1 if closing <= 0 else 0
        doi          = round(closing / max(dispatched, 1) * 30, 1) if dispatched > 0 else 999

        rows.append({
            'snapshot_id':      f'INV-{i:06d}',
            'snapshot_date':    snap_date.strftime('%Y-%m-%d'),
            'product_id':       prod_id,
            'warehouse_id':     wh_id,
            'opening_stock':    opening,
            'received_qty':     received,
            'dispatched_qty':   dispatched,
            'closing_stock':    closing,
            'stockout_flag':    stockout,
            'days_of_inventory': doi,
        })

    df = pd.DataFrame(rows)
    path = os.path.join(RAW_DIR, 'inventory.csv')
    df.to_csv(path, index=False)
    print(f"  ✓ inventory.csv saved — Shape: {df.shape}")
    print(df.head(3).to_string())
    return df


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 65)
    print("  SUPPLY CHAIN & LOGISTICS — DATA GENERATION PIPELINE")
    print("=" * 65)

    products   = generate_products(500)
    suppliers  = generate_suppliers(200)
    warehouses = generate_warehouses(20)
    orders     = generate_orders(products, suppliers, warehouses, 50000)
    inventory  = generate_inventory(products, warehouses, 10000)

    total = len(products) + len(suppliers) + len(warehouses) + len(orders) + len(inventory)
    print("\n" + "=" * 65)
    print(f"  DATA GENERATION COMPLETE!")
    print(f"  Total records generated : {total:,}")
    print(f"  Files saved to          : {RAW_DIR}")
    print("=" * 65)
