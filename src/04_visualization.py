# =============================================================================
# PROJECT  : Supply Chain & Logistics Analytics
# SCRIPT   : 04_visualization.py
# AUTHOR   : Chetan
# DESC     : Generates 8-panel executive dashboard
#            Output: reports/supply_chain_dashboard.png (300 DPI)
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
REPORTS_DIR   = os.path.join(BASE_DIR, 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# ── Color Palette ─────────────────────────────────────────────
C_BLUE   = '#2196F3'
C_GREEN  = '#4CAF50'
C_ORANGE = '#FF5722'
C_PURPLE = '#9C27B0'
C_TEAL   = '#009688'
C_AMBER  = '#FFC107'
PALETTE  = [C_BLUE, C_GREEN, C_ORANGE, C_PURPLE, C_TEAL, C_AMBER]


def load_data():
    orders     = pd.read_csv(os.path.join(PROCESSED_DIR, 'cleaned_orders.csv'), parse_dates=['order_date'])
    suppliers  = pd.read_csv(os.path.join(PROCESSED_DIR, 'cleaned_suppliers.csv'))
    warehouses = pd.read_csv(os.path.join(PROCESSED_DIR, 'cleaned_warehouses.csv'))
    inventory  = pd.read_csv(os.path.join(PROCESSED_DIR, 'cleaned_inventory.csv'), parse_dates=['snapshot_date'])
    products   = pd.read_csv(os.path.join(PROCESSED_DIR, 'cleaned_products.csv'))
    return orders, suppliers, warehouses, inventory, products


def create_dashboard():
    orders, suppliers, warehouses, inventory, products = load_data()

    sns.set_style('whitegrid')
    fig, axes = plt.subplots(4, 2, figsize=(22, 28))
    fig.patch.set_facecolor('#F8F9FA')

    # Main title
    fig.suptitle(
        'Supply Chain & Logistics Analytics Dashboard  |  FY 2023–24\nAuthor: Chetan  |  Data Analyst Portfolio Project',
        fontsize=18, fontweight='bold', y=0.98, color='#1A237E'
    )

    # ── PANEL 1: Top 10 Suppliers by On-Time Delivery Rate ────
    ax = axes[0, 0]
    top10 = suppliers.nlargest(10, 'on_time_delivery_rate')[['supplier_name', 'on_time_delivery_rate']]
    top10['supplier_short'] = top10['supplier_name'].str[:30]
    colors_p1 = [C_GREEN if x >= 90 else (C_AMBER if x >= 80 else C_ORANGE) for x in top10['on_time_delivery_rate']]
    bars = ax.barh(top10['supplier_short'], top10['on_time_delivery_rate'], color=colors_p1, edgecolor='white', height=0.7)
    ax.set_xlabel('On-Time Delivery Rate (%)', fontsize=10)
    ax.set_title('Top 10 Suppliers — On-Time Delivery Rate', fontweight='bold', fontsize=12, pad=10)
    ax.set_xlim(0, 105)
    for bar, val in zip(bars, top10['on_time_delivery_rate']):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f'{val:.1f}%', va='center', fontsize=9, fontweight='bold')
    ax.axvline(90, color='red', linestyle='--', linewidth=1, alpha=0.5, label='90% Benchmark')
    ax.legend(fontsize=9)
    ax.tick_params(axis='y', labelsize=8)

    # ── PANEL 2: Monthly Order Volume ─────────────────────────
    ax = axes[0, 1]
    monthly = orders.groupby(orders['order_date'].dt.to_period('M')).size().reset_index()
    monthly.columns = ['month', 'order_count']
    monthly['month_str'] = monthly['month'].astype(str)
    ax.plot(monthly['month_str'], monthly['order_count'], color=C_BLUE, linewidth=2.5, marker='o', markersize=5)
    ax.fill_between(monthly['month_str'], monthly['order_count'], alpha=0.15, color=C_BLUE)
    # Trend line
    z = np.polyfit(range(len(monthly)), monthly['order_count'], 1)
    p = np.poly1d(z)
    ax.plot(monthly['month_str'], p(range(len(monthly))), 'r--', linewidth=1.5, alpha=0.7, label='Trend')
    ax.set_xlabel('Month', fontsize=10)
    ax.set_ylabel('Order Count', fontsize=10)
    ax.set_title('Monthly Order Volume (Jan 2023 – Sep 2024)', fontweight='bold', fontsize=12, pad=10)
    ax.tick_params(axis='x', rotation=45, labelsize=7)
    ax.legend(fontsize=9)

    # ── PANEL 3: Freight Mode Share (Pie) ─────────────────────
    ax = axes[1, 0]
    mode_counts = orders['freight_mode'].value_counts()
    wedge_colors = [C_BLUE, C_GREEN, C_ORANGE, C_PURPLE]
    wedges, texts, autotexts = ax.pie(
        mode_counts.values, labels=mode_counts.index,
        autopct='%1.1f%%', colors=wedge_colors,
        startangle=90, pctdistance=0.75,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    for at in autotexts:
        at.set_fontsize(10); at.set_fontweight('bold')
    ax.set_title('Order Distribution by Freight Mode', fontweight='bold', fontsize=12, pad=10)

    # ── PANEL 4: Freight Cost per KG by Mode ──────────────────
    ax = axes[1, 1]
    mode_cost = orders.groupby('freight_mode')['freight_cost_per_kg'].mean().sort_values(ascending=False)
    bar_colors = [C_ORANGE if m == 'Air' else (C_BLUE if m == 'Road' else
                  (C_GREEN if m == 'Rail' else C_PURPLE)) for m in mode_cost.index]
    bars = ax.bar(mode_cost.index, mode_cost.values, color=bar_colors, edgecolor='white', width=0.6)
    ax.set_xlabel('Freight Mode', fontsize=10)
    ax.set_ylabel('Avg Cost per KG (₹)', fontsize=10)
    ax.set_title('Average Freight Cost per KG by Transport Mode', fontweight='bold', fontsize=12, pad=10)
    for bar, val in zip(bars, mode_cost.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f'₹{val:.1f}', ha='center', fontsize=11, fontweight='bold', color='#333')

    # ── PANEL 5: Warehouse Utilization Heatmap ────────────────
    ax = axes[2, 0]
    wh_data = warehouses[['warehouse_name', 'region', 'current_utilization_pct']].copy()
    wh_data['wh_short'] = wh_data['warehouse_name'].str[:20]
    pivot = wh_data.pivot_table(index='region', columns='wh_short',
                                 values='current_utilization_pct', aggfunc='mean')
    sns.heatmap(pivot, ax=ax, cmap='RdYlGn_r', annot=True, fmt='.0f', linewidths=0.5,
                cbar_kws={'label': 'Utilization %'}, annot_kws={'size': 7})
    ax.set_title('Warehouse Utilization by Region (%)', fontweight='bold', fontsize=12, pad=10)
    ax.set_xlabel('Warehouse', fontsize=9)
    ax.set_ylabel('Region', fontsize=9)
    ax.tick_params(axis='x', rotation=45, labelsize=7)
    ax.tick_params(axis='y', rotation=0, labelsize=8)

    # ── PANEL 6: Dead Stock Products ──────────────────────────
    ax = axes[2, 1]
    dead_products = products.merge(
        inventory.groupby('product_id').agg(
            total_dispatched=('dispatched_qty', 'sum'),
            avg_closing=('closing_stock', 'mean')
        ).reset_index(), on='product_id', how='left'
    )
    dead_products['turnover'] = dead_products['total_dispatched'] / dead_products['avg_closing'].replace(0, np.nan)
    dead = dead_products[dead_products['turnover'] < 2].nlargest(10, 'avg_closing')
    dead['prod_short'] = dead['product_name'].str[:25]
    ax.barh(dead['prod_short'], dead['avg_closing'], color=C_ORANGE, edgecolor='white')
    ax.set_xlabel('Avg Closing Stock (Units)', fontsize=10)
    ax.set_title('Top 10 Dead Stock Products (Turnover < 2x)', fontweight='bold', fontsize=12, pad=10)
    ax.tick_params(axis='y', labelsize=8)

    # ── PANEL 7: Delivery Performance by Freight Mode ─────────
    ax = axes[3, 0]
    perf_counts = orders.groupby(['freight_mode', 'delivery_performance']).size().unstack(fill_value=0)
    perf_pct = perf_counts.div(perf_counts.sum(axis=1), axis=0) * 100
    perf_colors = {'Early': C_TEAL, 'On-Time': C_GREEN, 'Slightly Late': C_AMBER, 'Very Late': C_ORANGE}
    bottom = np.zeros(len(perf_pct))
    for status in ['Early', 'On-Time', 'Slightly Late', 'Very Late']:
        if status in perf_pct.columns:
            vals = perf_pct[status].values
            ax.bar(perf_pct.index, vals, bottom=bottom, label=status,
                   color=perf_colors.get(status, C_BLUE), edgecolor='white')
            bottom += vals
    ax.set_ylabel('Percentage (%)', fontsize=10)
    ax.set_title('Delivery Performance by Freight Mode', fontweight='bold', fontsize=12, pad=10)
    ax.legend(loc='upper right', fontsize=8)
    ax.set_ylim(0, 100)

    # ── PANEL 8: Inventory Stockout Events by Month ───────────
    ax = axes[3, 1]
    monthly_stockout = inventory.groupby(inventory['snapshot_date'].dt.to_period('M'))['stockout_flag'].sum().reset_index()
    monthly_stockout.columns = ['month', 'stockout_count']
    monthly_stockout['month_str'] = monthly_stockout['month'].astype(str)
    ax.bar(monthly_stockout['month_str'], monthly_stockout['stockout_count'],
           color=C_ORANGE, edgecolor='white', alpha=0.85)
    ax.plot(monthly_stockout['month_str'], monthly_stockout['stockout_count'],
            color='darkred', linewidth=2, marker='D', markersize=5)
    ax.set_xlabel('Month', fontsize=10)
    ax.set_ylabel('Stockout Events', fontsize=10)
    ax.set_title('Monthly Inventory Stockout Events', fontweight='bold', fontsize=12, pad=10)
    ax.tick_params(axis='x', rotation=45, labelsize=7)

    # ── Save ──────────────────────────────────────────────────
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out_path = os.path.join(REPORTS_DIR, 'supply_chain_dashboard.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='#F8F9FA')
    plt.close()
    print(f"✓ Dashboard saved → {out_path}")


if __name__ == '__main__':
    print("=" * 65)
    print("  SUPPLY CHAIN — DASHBOARD GENERATION")
    print("=" * 65)
    create_dashboard()
    print("✓ All visualizations complete!")
