import streamlit as st
import pandas as pd
import os
import yfinance as yf

# =====================================================================
# 1. INTEGRATION: CONNECT TO YOUR MASTER PORTFOLIO BACKEND
# =====================================================================
def get_live_portfolio_total():
    """
    Placeholder: Replace the return value below with your actual function 
    that aggregates live balances across your master inventory database.
    """
    return 796576.07  # Matches your current master ledger total perfectly

# =====================================================================
# 2. CORE MATHEMATICAL ENGINES
# =====================================================================
def calculate_perpetual_freedom_score(
    portfolio_value, 
    base_expenses, 
    disc_expenses, 
    swr=0.035
):
    """Calculates traditional freedom score based on SWR."""
    safe_annual_income = portfolio_value * swr
    
    # Phase 1: Baseline Security (Score 0-50)
    if safe_annual_income < base_expenses:
        score = (safe_annual_income / base_expenses) * 50
    # Phase 2: Total Freedom (Score 51-100)
    else:
        base_score = 50
        if disc_expenses > 0:
            disc_coverage = (
                (safe_annual_income - base_expenses) / disc_expenses
            )
            score = base_score + (min(disc_coverage, 1.0) * 50)
        else:
            score = 100.0
            
    return round(score, 1), safe_annual_income

def calculate_household_bridge(
    portfolio_value, 
    total_annual_needs, 
    y_me, 
    y_wife, 
    p_me, 
    p_wife
):
    """Calculates time-horizon escrow required to bridge to pensions."""
    phase_1_duration = y_me
    phase_2_duration = max(0, y_wife - y_me)

    # Phase 1 Drawdown Total (Both off, zero pensions active)
    p1_total_cost = phase_1_duration * total_annual_needs

    # Phase 2 Drawdown Total (Your pension active, wife waiting)
    p2_annual_needs = max(0, total_annual_needs - p_me)
    p2_total_cost = phase_2_duration * p2_annual_needs

    # Total Escrow Required to completely buy out both timelines
    total_bridge_needed = p1_total_cost + p2_total_cost

    # Calculate Household Health Score (0 - 100%)
    if total_bridge_needed > 0:
        score = min((portfolio_value / total_bridge_needed) * 100, 100.0)
    else:
        score = 100.0

    return (
        round(score, 1), 
        total_bridge_needed, 
        p1_total_cost, 
        p2_total_cost, 
        phase_1_duration, 
        phase_2_duration, 
        p2_annual_needs
    )

# =====================================================================
# 3. UI LAYOUT & CONTROL SIDEBAR
# =====================================================================
st.set_page_config(layout="wide", page_title="Household Freedom Cockpit")
st.title("Outside Cup // Household Freedom Cockpit")
st.markdown("---")

# Sidebar Configuration - Formatted ultra-narrow to prevent web clipping
st.sidebar.header("🎛️ Lifestyle & Expense Controls")
base_expenses = st.sidebar.number_input(
    label="Annual Fixed Bills ($)", 
    value=45000, 
    step=1000
)
disc_expenses = st.sidebar.number_input(
    label="Annual Discretionary ($)", 
    value=25000, 
    step=1000
)
total_annual_needs = base_expenses + disc_expenses

st.sidebar.markdown("---")
st.sidebar.header("🧓 Pension Timeline Settings")
years_to_my_pension = st.sidebar.number_input(
    label="Years until MY pension starts", 
    value=8, 
    step=1
)
years_to_wife_pension = st.sidebar.number_input(
    label="Years until WIFE's pension starts", 
    value=18, 
    step=1
)

my_annual_pension = st.sidebar.number_input(
    label="My Estimated Annual Pension ($)", 
    value=35000, 
    step=1000
)
wife_annual_pension = st.sidebar.number_input(
    label="Wife's Estimated Annual Pension ($)", 
    value=25000, 
    step=1000
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ SWR Model (Traditional)")
swr_pct = st.sidebar.slider(
    label="Safe Withdrawal Rate (%)", 
    min_value=3.0, max_value=5.0, value=3.5, step=0.05
)
swr = swr_pct / 100

st.sidebar.markdown("---")
# Simulation Toggle Engine
enable_simulation = st.sidebar.checkbox(
    label="Enable Simulation Mode", 
    value=False
)

if enable_simulation:
    portfolio_value = st.sidebar.number_input(
        label="Simulated Portfolio Value ($)", 
        value=get_live_portfolio_total(), 
        step=10000
    )
    st.sidebar.caption("⚠️ Running in Simulation Mode")
else:
    portfolio_value = get_live_portfolio_total()
    st.sidebar.caption("⚡ Connected to Live Master Portfolio Data")

# =====================================================================
# 4. EXECUTE CALCULATIONS
# =====================================================================
# Model 1: Traditional Perpetual SWR
perpetual_score, safe_annual_income = calculate_perpetual_freedom_score(
    portfolio_value, 
    base_expenses, 
    disc_expenses, 
    swr
)
daily_safe_income = safe_annual_income / 365

# Model 2: Dynamic Multi-Stage Bridge Escrow
(
    household_score, 
    total_escrow_needed, 
    p1_total, 
    p2_total, 
    p1_dur, 
    p2_dur, 
    p2_ann
) = calculate_household_bridge(
    portfolio_value, 
    total_annual_needs, 
    years_to_my_pension, 
    years_to_wife_pension, 
    my_annual_pension, 
    wife_annual_pension
)

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
        st.write("TOTAL BRIDGE REQUIRED")
        st.subheader(f"${total_escrow_needed:,.2f}")
        st.caption("Liability Escrow Needed")

with col4:
    with st.container(border=True):
        st.write("PASSIVE DAILY INFLUX")
        st.subheader(f"${daily_safe_income:,.2f}/day")
        st.caption(f"Based on {swr_pct}% SWR")

st.markdown("---")

# =====================================================================
# 6. DETAILED TIMELINE BRIDGE ANALYSIS
# =====================================================================
st.subheader("🌉 Dynamic Household Freedom Bridge Breakdown")
st.progress(household_score / 100.0)

st.markdown("### 🗓️ Phase-by-Phase Capital Allocation")
col_p1, col_p2 = st.columns(2)

with col_p1:
    st.info(
        f"**Phase 1: Immediate Total Freedom ({p1_dur} Years)**\n\n"
        f"* **Household Status:** Both off, zero active pensions.\n"
        f"* **Annual Portfolio Target:** `${total_annual_needs:,.2f}/yr`\n"
        f"* **Total Phase Capital Allocated:** `${p1_total:,.2f}`"
    )

with col_p2:
    if p2_dur > 0:
        st.warning(
            f"**Phase 2: Partial Pension Relief ({p2_dur} Years)**\n\n"
            f"* **Household Status:** Your pension live, wife bridging timeline.\n"
            f"* **Annual Portfolio Target:** `${p2_ann:,.2f}/yr` (Net of your pension)\n"
            f"* **Total Phase Capital Allocated:** `${p2_total:,.2f}`"
        )
    else:
        st.success("No Phase 2 gap detected based on current timeline settings.")

# Decision Engine Output
if household_score >= 100:
    st.success("🟢 **SYSTEM STATUS: GO.** Your current portfolio has fully pre-funded the total multi-stage liability pool required to safely step away together today.")
else:
    gap_dollar = total_escrow_needed - portfolio_value
    st.error(f"🔴 **PORTFOLIO DEPLOYMENT GAP:** Your portfolio requires an additional **${gap_dollar:,.2f}** to completely secure her 18-year bridge timeline today.")

# =====================================================================
# 7. TRADITIONAL PERPETUAL COMPARISON (CONTEXT EXPANDER)
# =====================================================================
st.markdown("---")
with st.expander("📊 View Traditional Perpetual Retirement Comparison (SWR Baseline)"):
    st.caption("Tracks your portfolio assuming it had to sustain your lifestyle forever without any future pension cash flows.")
    st.progress(perpetual_score / 100.0)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Traditional SWR Score:** `{perpetual_score}%`")
        st.markdown(f"**Safe Annual Influx Generated:** `${safe_annual_income:,.2f}/year`")
    with c2:
        bill_coverage_pct = min((safe_annual_income / base_expenses) * 100, 100.0)
        st.markdown(f"**Fixed Bill Coverage Status:** `{bill_coverage_pct:.1f}%`")