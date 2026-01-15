import streamlit as st
import pandas as pd
import numpy as np

# ============================
# Load SuperMart Data
# ============================
df = pd.read_csv("SampleSuperStore_clean.csv")

# Clean data
df = df.replace([np.inf, -np.inf], np.nan).dropna()
df["Profit_per_Unit"] = df["Profit"] / df["Quantity"]

st.set_page_config(page_title="SuperMart Profit Engine", layout="wide")

st.title("🧠 SuperMart – Real-Time Profit Decision Engine")
st.caption("A functional prototype of the ERP + Pricing + Logistics control system")

# ============================
# User Inputs
# ============================
st.sidebar.header("Simulate an Order")

sku = st.sidebar.selectbox("Sub-Category", sorted(df["Sub-Category"].unique()))
region = st.sidebar.selectbox("Region", sorted(df["Region"].unique()))
discount = st.sidebar.slider("Discount %", 0, 50, 10) / 100

ship_type = st.sidebar.selectbox("Shipping Type", sorted(df["Ship_Type"].unique()))

# ============================
# Filter historical data
# ============================
f = df[(df["Sub-Category"] == sku) & (df["Region"] == region)]

if len(f) == 0:
    st.error("No historical data for this SKU & Region")
    st.stop()

# ============================
# Real economics from history
# ============================
base_price = f["Sales"].sum() / f["Quantity"].sum()
historical_profit = f["Profit"].sum() / f["Quantity"].sum()
base_cost = base_price - historical_profit

# ============================
# Realistic Shipping Cost
# ============================
region_base_cost = {
    "East": 8,
    "West": 6,
    "Central": 7,
    "South": 5
}

ship_multiplier = {
    "Standard": 1.0,
    "Second": 1.4,
    "First": 1.8
}

shipping_cost = region_base_cost.get(region, 6) * ship_multiplier.get(ship_type, 1.0)
shipping_cost = round(shipping_cost, 2)

# ============================
# Apply Discount
# ============================
final_price = base_price * (1 - discount)

# ============================
# Final Profit & Margin
# ============================
profit = final_price - base_cost - shipping_cost
margin = profit / final_price

# ============================
# Real Business Rules
# ============================
sku_margin_rules = {
    "Technology": 0.12,
    "Furniture": 0.10,
    "Office Supplies": 0.08
}

region_margin_rules = {
    "East": 0.12,
    "West": 0.10,
    "Central": 0.10,
    "South": 0.09
}

category = f["Category"].iloc[0]
min_margin = max(
    sku_margin_rules.get(category, 0.08),
    region_margin_rules.get(region, 0.08)
)

# ============================
# Decision Engine
# ============================
decision = "APPROVED"
reason = "Meets all margin and profitability rules"

if profit < 0:
    decision = "REJECTED"
    reason = "Loss-making order"

elif margin < min_margin:
    decision = "REJECTED"
    reason = f"Below required margin of {int(min_margin*100)}% for {category} in {region}"

# ============================
# Display Results
# ============================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Base Price", f"₹{base_price:,.2f}")
col2.metric("Final Price", f"₹{final_price:,.2f}")
col3.metric("Profit / Unit", f"₹{profit:,.2f}")
col4.metric("Margin", f"{margin*100:.1f}%")

st.subheader("Decision")

if decision == "APPROVED":
    st.success("✅ ORDER APPROVED")
else:
    st.error("❌ ORDER REJECTED")

st.write("**Reason:**", reason)

# ============================
# Transparency Layer
# ============================
st.subheader("How the system decided")

explain = pd.DataFrame({
    "Metric": [
        "Category", "Region", "Shipping Type",
        "Base Price", "Base Cost",
        "Discount", "Shipping Cost",
        "Final Price", "Profit", "Margin",
        "Required Margin"
    ],
    "Value": [
        category, region, ship_type,
        round(base_price,2),
        round(base_cost,2),
        f"{int(discount*100)}%",
        shipping_cost,
        round(final_price,2),
        round(profit,2),
        f"{round(margin*100,1)}%",
        f"{int(min_margin*100)}%"
    ]
})

st.dataframe(explain, use_container_width=True)
