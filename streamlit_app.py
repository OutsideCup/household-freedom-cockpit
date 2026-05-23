import streamlit as st
import pandas as pd

# =====================================================================
# 1. CORE MATHEMATICAL ENGINES (Defined first so they exist)
# =====================================================================
def calculate_perpetual_freedom_score(portfolio_value, base_expenses, disc_expenses, swr=0.035):
    safe_annual_income = portfolio_value * swr
    if safe_annual_income < base_expenses:
        score = (safe_annual_income / base_expenses) * 50
    else:
        base_score = 50
        if disc_expenses > 0:
            disc_coverage = ((safe_annual_income - base_expenses) / disc_expenses)
            score = base_score + (min(disc_coverage, 1.0) * 50)
        else:
            score = 100.0
    return round(score, 1), safe_annual_income

def calculate_household_bridge(portfolio_value, total_annual_needs, y_me, y_wife, p_me, p_wife):
    phase_1_duration = y_me
    phase_2_duration = max(0, y_wife - y_me)
    p1_total_cost = phase_1_duration * total_annual_needs
    p2_annual_needs = max(0, total_annual_needs - p_me)
    p2_total_cost = phase_2_duration * p2_annual_needs
    total_bridge_needed = p1_total_cost + p2_total_cost
    score = min((portfolio_value / total_bridge_needed) * 100, 100.0) if total_bridge_needed > 0 else 100.0
    return (round(score, 1), total_bridge_needed, p1_total_cost, p2_total_cost, phase_1_duration, phase_2_duration, p2_annual_needs)

# =====================================================================
# 2. UI LAYOUT & SIDEBAR
# =====================================================================
st.set_page_config(layout="wide", page_title="Household Freedom Cockpit")
st.title("Outside Cup // Household Freedom Cockpit")
st.markdown("---")

# Sidebar inputs
st.sidebar.header("🎛️ Lifestyle & Expense Controls")
base_expenses = st.sidebar.number_input("Annual Fixed Bills ($)", value=45000, step=1000)
disc_expenses = st.sidebar.number_input("Annual Discretionary ($)", value=25000, step=1000)
total_annual_needs = base_expenses + disc_expenses

st.sidebar.markdown("---")
st.sidebar.header("🧓 Pension Timeline Settings")
y_me = st.sidebar.number_input("Years until MY pension starts", value=8, step=1)
y_wife = st.sidebar.number_input("Years until WIFE's pension starts", value=18, step=1)
p_me = st.sidebar.number_input("My Estimated Annual Pension ($)", value=35000, step=1000)
p_wife = st.sidebar.number_input("Wife's Estimated Annual Pension ($)", value=25000, step=1000)

st.sidebar.markdown("---")
st.sidebar.header("📈 Manual Portfolio Update")

# The "Safe" Form approach
with st.sidebar.form("portfolio_form"):
    manual_val = st.number_input("Enter Today's Total ($)", value=796576.07, step=1000.0, format="%.2f")
    submitted = st.form_submit_button("Update Cockpit")

# If button is clicked, use manual_val, otherwise default to fixed
if submitted:
    portfolio_value = manual_val
    st.sidebar.success("Override active.")
else:
    portfolio_value = 796576.07

# =====================================================================
# 3. CALCULATIONS & RENDER (Must be after definitions)
# =====================================================================
perpetual_score, safe_annual_income = calculate_perpetual_freedom_score(portfolio_value, base_expenses, disc_expenses)
(household_score, total_escrow, p1_t, p2_t, p1_d, p2_d, p2_ann) = calculate_household_bridge(portfolio_value, total_annual_needs, y_me, y_wife, p_me, p_wife)

col1, col2, col3, col4 = st.columns(4)
col1.metric("HEALTH SCORE", f"{household_score}%")
col2.metric("LIQUID ASSETS", f"${portfolio_value:,.2f}")
col3.metric("BRIDGE REQUIRED", f"${total_escrow:,.2f}")
col4.metric("DAILY INFLUX", f"${(safe_annual_income/365):,.2f}/day")

st.markdown("---")
st.subheader("🌉 Dynamic Household Freedom Bridge Breakdown")
st.progress(household_score / 100.0)

c1, c2 = st.columns(2)
c1.info(f"**Phase 1: {p1_d} Years**\n\nTotal Capital: ${p1_t:,.2f}")
c2.warning(f"**Phase 2: {p2_d} Years**\n\nTotal Capital: ${p2_t:,.2f}")
