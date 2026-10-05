-- ============================================================
-- PROJECT  : Supply Chain & Logistics Analytics
-- AUTHOR   : Chetan
-- DATABASE : supplychain_db
-- DESC     : 10 Real Business Problems solved using MySQL
--            Tables: products, suppliers, warehouses, orders, inventory
--            Total Records: 60,000+
--            Time Period: Jan 2023 – Sep 2024
-- ============================================================

CREATE DATABASE IF NOT EXISTS supplychain_db;
USE supplychain_db;

-- ============================================================
-- PROBLEM 1: Overall Supply Chain Health Dashboard
-- Business Use: Give leadership a single-view KPI summary
--               of supply chain performance.
-- ============================================================
SELECT
    COUNT(*)                                              AS Total_Orders,
    ROUND(AVG(fulfillment_rate), 2)                       AS Avg_Fulfillment_Rate_Pct,
    ROUND(AVG(CASE WHEN delay_days > 0 THEN delay_days END), 2) AS Avg_Delay_Days_When_Late,
    SUM(CASE WHEN delivery_status = 'On-Time' THEN 1 ELSE 0 END) AS OnTime_Orders,
    ROUND(SUM(CASE WHEN delivery_status='On-Time' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
                                                          AS OnTime_Rate_Pct,
    ROUND(SUM(freight_cost_inr), 2)                       AS Total_Freight_Cost_INR,
    ROUND(SUM(total_cost_inr), 2)                         AS Total_Order_Value_INR,
    ROUND(SUM(freight_cost_inr) / SUM(total_cost_inr) * 100, 2)
                                                          AS Freight_As_Pct_Of_Value
FROM orders;
-- Expected: OnTime rate ~70-80%, Freight ~5-15% of value


-- ============================================================
-- PROBLEM 2: Top 10 Suppliers by On-Time Delivery Rate
-- Business Use: Identify reliable vendor partners for
--               preferred supplier agreements and priority allocation.
-- ============================================================
SELECT
    s.supplier_id,
    s.supplier_name,
    s.city,
    s.region,
    s.quality_rating,
    s.on_time_delivery_rate                                AS Supplier_OTD_Rate,
    COUNT(o.order_id)                                      AS Total_Orders,
    ROUND(AVG(o.delay_days), 2)                            AS Avg_Delay_Days,
    ROUND(SUM(o.total_cost_inr), 0)                        AS Total_Order_Value_INR,
    ROUND(SUM(CASE WHEN o.delivery_status='On-Time' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
                                                           AS Actual_OTD_Pct
FROM suppliers s
JOIN orders o ON s.supplier_id = o.supplier_id
GROUP BY s.supplier_id, s.supplier_name, s.city, s.region, s.quality_rating, s.on_time_delivery_rate
ORDER BY Actual_OTD_Pct DESC
LIMIT 10;
-- Expected: Top suppliers show >90% OTD, based in Mumbai/Delhi/Bengaluru


-- ============================================================
-- PROBLEM 3: Monthly Demand vs Supply Gap Analysis
-- Business Use: Identify which months had critical supply
--               shortfalls to inform procurement planning.
-- ============================================================
SELECT
    DATE_FORMAT(order_date, '%Y-%m')                      AS Order_Month,
    SUM(quantity_ordered)                                  AS Total_Demand_Units,
    SUM(quantity_received)                                 AS Total_Supply_Units,
    SUM(quantity_ordered) - SUM(quantity_received)        AS Supply_Gap_Units,
    ROUND((SUM(quantity_ordered) - SUM(quantity_received)) * 100.0 / SUM(quantity_ordered), 2)
                                                          AS Gap_Percentage,
    ROUND(AVG(fulfillment_rate), 2)                        AS Avg_Fulfillment_Rate,
    COUNT(order_id)                                        AS Total_Orders
FROM orders
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY Gap_Percentage DESC;
-- Expected: Some months show 8-15% supply gap — useful for pre-festival inventory


-- ============================================================
-- PROBLEM 4: Freight Cost Optimization — Mode Analysis
-- Business Use: Quantify the financial impact of switching
--               high-cost freight modes (Air → Road/Rail).
-- ============================================================
SELECT
    freight_mode,
    COUNT(order_id)                                        AS Total_Shipments,
    ROUND(AVG(freight_cost_per_kg), 2)                     AS Avg_Cost_Per_KG_INR,
    ROUND(SUM(freight_cost_inr), 0)                        AS Total_Freight_Spend_INR,
    ROUND(SUM(freight_cost_inr) * 100.0 / SUM(SUM(freight_cost_inr)) OVER (), 2)
                                                           AS Share_Of_Total_Freight_Pct,
    ROUND(AVG(delay_days), 2)                              AS Avg_Delay_Days
FROM orders
GROUP BY freight_mode
ORDER BY Total_Freight_Spend_INR DESC;
-- Expected: Air is <10% volume but 40%+ of freight cost — optimization opportunity


-- ============================================================
-- PROBLEM 5: Warehouse Capacity Utilization & Overload Risk
-- Business Use: Identify overloaded warehouses that need
--               capacity expansion or redistribution.
-- ============================================================
SELECT
    w.warehouse_id,
    w.warehouse_name,
    w.city,
    w.region,
    w.capacity_units,
    w.current_utilization_pct,
    CASE
        WHEN w.current_utilization_pct > 85 THEN 'OVERLOADED ⚠️'
        WHEN w.current_utilization_pct > 70 THEN 'HIGH'
        ELSE 'NORMAL'
    END                                                    AS Utilization_Status,
    COUNT(o.order_id)                                      AS Orders_Handled,
    ROUND(SUM(o.total_cost_inr), 0)                        AS Total_Value_Handled_INR
FROM warehouses w
LEFT JOIN orders o ON w.warehouse_id = o.warehouse_id
GROUP BY w.warehouse_id, w.warehouse_name, w.city, w.region,
         w.capacity_units, w.current_utilization_pct
ORDER BY w.current_utilization_pct DESC;
-- Expected: 3-5 warehouses flagged as OVERLOADED


-- ============================================================
-- PROBLEM 6: Dead Stock Identification
-- Business Use: Flag slow-moving products tying up working
--               capital — candidates for liquidation/discount.
-- ============================================================
SELECT
    i.product_id,
    p.product_name,
    p.category,
    p.unit_price_inr,
    ROUND(AVG(i.closing_stock), 0)                         AS Avg_Stock_Units,
    SUM(i.dispatched_qty)                                  AS Total_Dispatched_Units,
    ROUND(SUM(i.dispatched_qty) / NULLIF(AVG(i.closing_stock), 0), 2)
                                                           AS Inventory_Turnover,
    ROUND(AVG(i.closing_stock) * p.unit_price_inr * 0.20, 0)
                                                           AS Annual_Holding_Cost_INR,
    COUNT(CASE WHEN i.stockout_flag = 1 THEN 1 END)        AS Stockout_Events
FROM inventory i
JOIN products p ON i.product_id = p.product_id
GROUP BY i.product_id, p.product_name, p.category, p.unit_price_inr
HAVING Inventory_Turnover < 2 OR Inventory_Turnover IS NULL
ORDER BY Annual_Holding_Cost_INR DESC
LIMIT 20;
-- Expected: 15-25% of SKUs are dead stock — high holding cost


-- ============================================================
-- PROBLEM 7: Delivery Delay Root Cause Analysis
-- Business Use: Identify which combination of freight mode
--               and supplier region causes most delays.
-- ============================================================
SELECT
    s.region                                               AS Supplier_Region,
    o.freight_mode,
    COUNT(o.order_id)                                      AS Total_Orders,
    ROUND(AVG(o.delay_days), 2)                            AS Avg_Delay_Days,
    ROUND(AVG(CASE WHEN o.delay_days > 0 THEN o.delay_days END), 2)
                                                           AS Avg_Delay_When_Late,
    SUM(CASE WHEN o.delay_days > 3 THEN 1 ELSE 0 END)     AS Severely_Late_Orders,
    ROUND(SUM(CASE WHEN o.delay_days > 3 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
                                                           AS Severe_Late_Rate_Pct
FROM orders o
JOIN suppliers s ON o.supplier_id = s.supplier_id
GROUP BY s.region, o.freight_mode
ORDER BY Avg_Delay_Days DESC;
-- Expected: Air from East region shows worst delay paradox


-- ============================================================
-- PROBLEM 8: Vendor Risk Classification
-- Business Use: Automatically segment vendors into risk tiers
--               for procurement policy decisions.
-- ============================================================
SELECT
    s.supplier_id,
    s.supplier_name,
    s.quality_rating,
    s.on_time_delivery_rate,
    COUNT(o.order_id)                                      AS Total_Orders,
    ROUND(SUM(o.total_cost_inr), 0)                        AS Total_Spend_INR,
    CASE
        WHEN s.on_time_delivery_rate >= 90 AND s.quality_rating >= 4.0 THEN 'PREFERRED ✅'
        WHEN s.on_time_delivery_rate >= 80 AND s.quality_rating >= 3.0 THEN 'STANDARD 🟡'
        WHEN s.on_time_delivery_rate >= 70 THEN 'AT-RISK 🔶'
        ELSE 'CRITICAL ❌'
    END                                                    AS Vendor_Tier,
    ROUND(AVG(o.delay_days), 2)                            AS Avg_Order_Delay_Days
FROM suppliers s
LEFT JOIN orders o ON s.supplier_id = o.supplier_id
GROUP BY s.supplier_id, s.supplier_name, s.quality_rating, s.on_time_delivery_rate
ORDER BY s.on_time_delivery_rate DESC;
-- Expected: ~30% Preferred, ~45% Standard, ~20% At-Risk, ~5% Critical


-- ============================================================
-- PROBLEM 9: Seasonal Demand Patterns by Product Category
-- Business Use: Align procurement and stocking strategy
--               with seasonal peaks (Diwali, summer, etc.).
-- ============================================================
SELECT
    p.category,
    MONTH(o.order_date)                                    AS Month_Number,
    MONTHNAME(o.order_date)                                AS Month_Name,
    COUNT(o.order_id)                                      AS Total_Orders,
    SUM(o.quantity_ordered)                                AS Total_Units_Ordered,
    ROUND(SUM(o.total_cost_inr), 0)                        AS Total_Value_INR
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.category, MONTH(o.order_date), MONTHNAME(o.order_date)
ORDER BY p.category, Month_Number;
-- Expected: Electronics peaks Oct-Nov (Diwali), FMCG peaks Jun-Aug (summer)


-- ============================================================
-- PROBLEM 10: Rolling 3-Month Average Freight Cost Trend
-- Business Use: Smooth out monthly volatility to identify
--               true freight cost trends using window functions.
-- ============================================================
WITH monthly_freight AS (
    SELECT
        DATE_FORMAT(order_date, '%Y-%m')                   AS order_month,
        freight_mode,
        ROUND(SUM(freight_cost_inr), 0)                    AS monthly_freight_inr,
        COUNT(order_id)                                    AS shipment_count,
        ROUND(AVG(freight_cost_per_kg), 2)                 AS avg_cost_per_kg
    FROM orders
    GROUP BY DATE_FORMAT(order_date, '%Y-%m'), freight_mode
)
SELECT
    order_month,
    freight_mode,
    monthly_freight_inr,
    avg_cost_per_kg,
    ROUND(AVG(monthly_freight_inr) OVER (
        PARTITION BY freight_mode
        ORDER BY order_month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 0)                                                  AS Rolling_3M_Avg_Freight_INR,
    ROUND(AVG(avg_cost_per_kg) OVER (
        PARTITION BY freight_mode
        ORDER BY order_month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2)                                                  AS Rolling_3M_Avg_Cost_Per_KG
FROM monthly_freight
ORDER BY freight_mode, order_month;
-- Expected: Smooth trend shows Air costs gradually rising; Road stable
