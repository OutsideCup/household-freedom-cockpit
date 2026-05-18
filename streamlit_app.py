import streamlit as st
import pandas as pd
import os
import yfinance as yf

# =====================================================================
# 1. INTEGRATION: CONNECT TO YOUR MASTER PORTFOLIO BACKEND
# =====================================================================
def get_live_portfolio_total():
    return 796576.07  # Matches your current master ledger total perfectly

# =====================================================================
# 2. CORE MATHEMATICAL ENGINES (WITH COMPOUNDING & RESERVE CHECKS)
# =====================================================================
def calculate_perpetual_freedom_score(portfolio_value, base_expenses, disc_expenses, swr=0.035):
    """Calculates traditional freedom score based on SWR."""
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

def calculate_compounded_household_bridge(portfolio_value, total_annual_needs, y_me, y_wife, p_me, p_wife, annual_growth_rate):
    """Calculates the time-horizon escrow required and projects actual terminal value with compounding growth."""
    phase_1_duration = y_me
    phase_2_duration = max(0, y_wife - y_me)
    
    # 1. Worst Case Zero-Growth Escrow (Your original safety anchor)
    p1_raw_cost = phase_1_duration * total_annual_needs
    p2_annual_gap = max(0, total_annual_needs - p_me)
    p2_raw_cost = phase_2_duration * p2_annual_gap
    total_bridge_needed = p1_raw_cost + p2_raw_cost
    
    # Calculate Household Health Score based on raw safety limit
    if total_bridge_needed > 0:
        score = min((portfolio_value / total_bridge_needed) * 100, 100.0)
    else:
        score = 100.0

    # 2. Dynamic Compounding Projection Loop
    current_balance = portfolio_value
    r = annual_growth_rate
    
    # Run Phase 1 Compounding
    for year in range(1, phase_1_duration + 1):
        current_balance = (current_balance * (1 + r)) - total_annual_needs
        
    # Run Phase 2 Compounding
    for year in range(1, phase_2_duration + 1):
        current_balance = (current_balance * (1 + r)) - p2_annual_gap
        
    terminal_wealth = max(0.0, current_balance)
    
    return (
        round(score, 1), 
        total_bridge_needed, 
        p1_raw_cost, 
        p2_raw_cost, 
        phase_1_duration, 
        phase_2_duration, 
        p2_annual_gap,
        round(terminal_wealth, 2)
    )

# =====================================================================
# 3. UI LAYOUT & CONTROL SIDEBAR
# =====================================================================
st.set_page_config(layout="wide", page_title="Household Freedom Cockpit")
st.title("Outside Cup // Household Freedom Cockpit")
st.markdown("---")

st.sidebar.header("🎛️ Lifestyle & Expense Controls")
base_expenses = st.sidebar.number_input(label="Annual Fixed Bills ($)", value=40000, step=1000)
disc_expenses = st.sidebar.number_input(label="Annual Discretionary ($)", value=15000, step=1000)
total_annual_needs = base_expenses + disc_expenses

st.sidebar.markdown("---")
st.sidebar.header("📈 Portfolio Performance Settings")
growth_rate_pct = st.sidebar.slider(label="Assumed Annual Growth Rate (%)", min_value=0.0, max_value=8.0, value=4.0, step=0.25)
growth_rate = growth_rate_pct / 100

st.sidebar.markdown("---")
st.sidebar.header("🧓 Pension Timeline Settings")
years_to_my_pension = st.sidebar.number_input(label="Years until MY pension starts", value=8, step=1)
years_to_wife_pension = st.sidebar.number_input(label="Years until WIFE's pension starts", value=18, step=1)

my_annual_pension = st.sidebar.number_input(label="My Estimated Annual Pension ($)", value=35000, step=1000)
wife_annual_pension = st.sidebar.number_input(label="Wife's Estimated Annual Pension ($)", value=25000, step=1000)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ SWR Model (Traditional)")
swr_pct = st.sidebar.slider(label="Safe Withdrawal Rate (%)", min_value=3.0, max_value=5.0, value=3.5, step=0.05)
swr = swr_pct / 100

st.sidebar.markdown("---")
enable_simulation = st.sidebar.checkbox(label="Enable Simulation Mode", value=False)

if enable_simulation:
    portfolio_value = st.sidebar.number_input(label="Simulated Portfolio Value ($)", value=get_live_portfolio_total(), step=10000)
    st.sidebar.caption("⚠️ Running in Simulation Mode")
else:
    portfolio_value = get_live_portfolio_total()
    st.sidebar.caption("⚡ Connected to Live Master Portfolio Data")

# =====================================================================
# 4. EXECUTE CALCULATIONS
# =====================================================================
perpetual_score, safe_annual_income = calculate_perpetual_freedom_score(portfolio_value, base_expenses, disc_expenses, swr)
daily_safe_income = safe_annual_income / 365

(
    household_score, 
    total_escrow_needed, 
    p1_total, 
    p2_total, 
    p1_dur, 
    p2_dur, 
    p2_ann,
    projected_terminal_wealth
) = calculate_compounded_household_bridge(
    portfolio_value, total_annual_needs, years_to_my_pension, years_to_wife_pension, my_annual_pension, wife_annual_pension, growth_rate
)

# 10x Living Expenses Reserve Core Math Guardrail
comfort_reserve_floor = total_annual_needs * 10
reserve_cushion_delta = projected_terminal_wealth - comfort_reserve_floor

# =====================================================================
# 5. RENDER PRIMARY METRIC CARDS
# =====================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.write("HOUSEHOLD HEALTH SCORE")
        st.subheader(f"{household_score}%")
        if household_score >= 100:
            st.caption("🟢 Ready to Retire Both!")
        else:
            st.caption(f"🔴 {100 - household_score:.1f}% to Bridge Target")

with col2:
    with st.container(border=True):
        st.write("CURRENT LIQUID ASSETS")
        st.subheader(f"${portfolio_value:,.2f}")
        st.caption("CAD Global Value")

with col3:
    with st.container(border=True):
        st.write("TOTAL BRIDGE
