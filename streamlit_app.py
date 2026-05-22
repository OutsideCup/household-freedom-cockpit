import streamlit as st
import pandas as pd

# =====================================================================
# 1. CORE MATHEMATICAL ENGINES
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

st.sidebar.header("🎛️ Lifestyle & Expense Controls")
base_expenses = st.sidebar.number_input("Annual Fixed Bills ($)", value=45000, step=1000)
disc_expenses = st.sidebar.number_input("Annual Discretionary ($)", value=25000, step=1000)
total_annual_needs = base_expenses + disc_expenses

st.sidebar.markdown("---")
st.sidebar.header("🧓 Pension Timeline")
y_me = st.sidebar.number_input("Years until MY pension", value=8, step=1)
y_wife = st.sidebar.number_input("Years until WIFE's pension", value=18, step=1)
p_me = st.sidebar.number_input("My Pension ($)", value=35000, step=1000)
p_wife = st.sidebar.number_input("Wife's Pension ($)", value=25000, step=1000)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ SWR Model")
swr_pct = st.sidebar.slider("Safe Withdrawal Rate (%)", 3.0, 5.0, 3.5, 0.05)
swr = swr_pct / 100

st.sidebar.markdown("---")
st.sidebar.header("📈 Portfolio Update")
portfolio_value = st.sidebar.number_input("Enter Current Total ($)", value=811006.77, step=1000.0, format="%.2f")

# =====================================================================
# 3. CALCULATIONS
# =====================================================================
perpetual_score, safe_annual_income = calculate_perpetual_freedom_score(portfolio_value, base_expenses, disc_expenses, swr)
(household_score, total_escrow, p1_t, p2_t, p1_d, p2_d, p2_ann) = calculate_household_bridge(portfolio_value, total_annual_needs, y
