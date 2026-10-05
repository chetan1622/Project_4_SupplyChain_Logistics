# =============================================================================
# PROJECT  : Supply Chain & Logistics Analytics
# SCRIPT   : 02_data_cleaning.py
# AUTHOR   : Chetan
# DESC     : Loads raw CSVs, performs cleaning & feature engineering,
#            saves cleaned files to data/processed/
# =============================================================================

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR       = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
os.makedirs(PROCESSED_DIR, exist_ok=True)


def load_data():
    print("Loading raw data...")
    dfs = {}
    for name in ['products', 'suppliers', 'warehouses', 'orders', 'inventory']:
        path = os.path.join(RAW_DIR, f'{name}.csv')
        dfs[name] = pd.read_csv(path)
        print(f"  ✓ {name}.csv — {dfs[name].shape}")
    return dfs


def clean_products(df):
    print("\n── Cleaning: products ──")
    before = len(df)
    df.drop_duplicates(inplace=True)
    df['unit_price_inr'] = df['unit_price_inr'].fillna(df['unit_price_inr'].median())
    df['weight_kg']      = df['weight_kg'].fillna(df['weight_kg'].median())
    df['lead_time_days'] = df['lead_time_days'].fillna(df['lead_time_days'].median()).astype(int)
    df['reorder_point']  = df['reorder_point'].fillna(50).astype(int)
    df['price_tier']     = pd.cut(df['unit_price_inr'],
                                   bins=[0, 500, 5000, 20000, float('inf')],
                                   labels=['Budget', 'Mid-Range', 'Premium', 'Luxury'])
    print(f"  Duplicates removed   : {before - len(df)}")
    print(f"  Null values remaining: {df.isnull().sum().sum()}")
    return df


def clean_suppliers(df):
    print("\n── Cleaning: suppliers ──")
    before = len(df)
    df.drop_duplicates(inplace=True)
    df['quality_rating']        = df['quality_rating'].fillna(df['quality_rating'].median())
    df['on_time_delivery_rate'] = df['on_time_delivery_rate'].fillna(df['on_time_delivery_rate'].median())
    df['supplier_tier'] = pd.cut(df['on_time_delivery_rate'],
                                  bins=[0, 75, 88, 100],
                                  labels=['At-Risk', 'Standard', 'Preferred'])
    print(f"  Duplicates removed   : {before - len(df)}")
    print(f"  Supplier tiers:\n{df['supplier_tier'].value_counts().to_string()}")
    return df


def clean_warehouses(df):
    print("\n── Cleaning: warehouses ──")
    df.drop_duplicates(inplace=True)
    df['utilization_status'] = df['current_utilization_pct'].apply(
        lambda x: 'Overloaded' if x > 85 else ('High' if x > 70 else 'Normal'))
    return df


def clean_orders(df):
    print("\n── Cleaning: orders ──")
    before = len(df)
    df.drop_duplicates(subset='order_id', inplace=True)
    df['order_date']            = pd.to_datetime(df['order_date'])
    df['expected_delivery_date']= pd.to_datetime(df['expected_delivery_date'])
    df['actual_delivery_date']  = pd.to_datetime(df['actual_delivery_date'])

    df['freight_cost_inr'] = df['freight_cost_inr'].fillna(df['freight_cost_inr'].median())
    df['unit_cost_inr']    = df['unit_cost_inr'].fillna(df['unit_cost_inr'].median())

    # Derived columns
    df['order_month']  = df['order_date'].dt.to_period('M').astype(str)
    df['order_year']   = df['order_date'].dt.year
    df['order_quarter']= df['order_date'].dt.quarter.map({1:'Q1',2:'Q2',3:'Q3',4:'Q4'})

    df['fulfillment_rate'] = (df['quantity_received'] / df['quantity_ordered'] * 100).round(2)
    df['fulfillment_rate'] = df['fulfillment_rate'].clip(0, 100)

    df['total_value_category'] = pd.cut(df['total_cost_inr'],
                                         bins=[0, 10000, 100000, float('inf')],
                                         labels=['Low', 'Medium', 'High'])

    df['delivery_performance'] = df['delay_days'].apply(
        lambda d: 'Early' if d < 0 else ('On-Time' if d == 0 else
                  ('Slightly Late' if d <= 3 else 'Very Late')))

    print(f"  Duplicates removed       : {before - len(df)}")
    print(f"  Delivery performance mix :\n{df['delivery_performance'].value_counts().to_string()}")
    print(f"  Freight mode mix         :\n{df['freight_mode'].value_counts().to_string()}")
    return df


def clean_inventory(df):
    print("\n── Cleaning: inventory ──")
    df.drop_duplicates(inplace=True)
    df['snapshot_date'] = pd.to_datetime(df['snapshot_date'])
    df['closing_stock']  = df['closing_stock'].clip(0)
    df['days_of_inventory'] = df['days_of_inventory'].clip(0, 999)

    df['stockout_risk'] = df['days_of_inventory'].apply(
        lambda d: 'Critical' if d < 7 else ('Warning' if d <= 14 else 'Safe'))
    return df


def print_cleaning_report(dfs_clean):
    print("\n" + "=" * 65)
    print("  DATA CLEANING SUMMARY REPORT")
    print("=" * 65)
    for name, df in dfs_clean.items():
        nulls = df.isnull().sum().sum()
        print(f"  {name:<12} | Rows: {len(df):>6,} | Cols: {len(df.columns):>3} | Nulls: {nulls}")
    print("=" * 65)


def save_cleaned(dfs_clean):
    print("\nSaving cleaned files to data/processed/ ...")
    for name, df in dfs_clean.items():
        path = os.path.join(PROCESSED_DIR, f'cleaned_{name}.csv')
        df.to_csv(path, index=False)
        print(f"  ✓ cleaned_{name}.csv saved")


if __name__ == '__main__':
    print("=" * 65)
    print("  SUPPLY CHAIN — DATA CLEANING PIPELINE")
    print("=" * 65)

    dfs = load_data()

    dfs_clean = {
        'products':   clean_products(dfs['products']),
        'suppliers':  clean_suppliers(dfs['suppliers']),
        'warehouses': clean_warehouses(dfs['warehouses']),
        'orders':     clean_orders(dfs['orders']),
        'inventory':  clean_inventory(dfs['inventory']),
    }

    print_cleaning_report(dfs_clean)
    save_cleaned(dfs_clean)
    print("\n✓ Data cleaning complete! Files saved to data/processed/")
