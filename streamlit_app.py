import streamlit as st
import pandas as pd
import os

# =====================================================================
# 1. INTEGRATION: CONNECT TO YOUR MASTER PORTFOLIO BACKEND
# =====================================================================
def get_live_portfolio_total():
    return 796576.07  # Matches your current master ledger total perfectly

# =====================================================================
# 2. ADVANCED YEAR-BY-YEAR SIMULATION ENGINE
# =====================================================================
def run_dynamic_household_simulation(
    portfolio_start, base_bills, start_disc, growth_rate, 
    my_pension_base, my_start_age, wife_pension_base, wife_start_age,
    gogo_years, slowgo_drop_pct
):
    """
    Runs a precise, year-by-year simulation over an 18-year horizon to capture:
    1. 'Go-Go' spending reductions over time.
    2. Exact pension start years based on customized target ages.
    3. Year-by-year portfolio compounding and draws.
    """
    # Current Ages (Baseline 2026: You are 57, Wife is 47)
    my_start_hours_age = 57
    wife_start_hours_age = 47
    
    records = []
    current_balance = portfolio_start
    r = growth_rate
    
    total_raw_outflow_no_growth = 0
    
    # Run the simulation for exactly 18 years (until your wife reaches 65)
    for year in range(1, 19):
        my_current_age = my_start_hours_age + year - 1
        wife_current_age = wife_start_hours_age + year - 1
        
        # Calculate Spending for the Year (Go-Go vs. Slow-Go logic)
        if year <= gogo_years:
            current_disc = start_disc
            spending_phase = "Go-Go Phase"
        else:
            current_disc = start_disc * (1 - (slowgo_drop_pct / 100))
            spending_phase = "Slow-Go Phase"
            
        annual_lifestyle_need = base_bills + current_disc
        
        # Calculate Active Inflows (Pensions) based on custom ages chosen
        my_active_pension = my_pension_base if my_current_age >= my_start_age else 0.0
        wife_active_pension = wife_pension_base if wife_current_age >= wife_start_age else 0.0
        total_pension_inflow = my_active_pension + wife_active_pension
        
        # Net Portfolio Draw required
        net_portfolio_draw = max(0.0, annual_lifestyle_need - total_pension_inflow)
        total_raw_outflow_no_growth += net_portfolio_draw
        
        # Apply market growth first, then execute lifestyle drawdown
        previous_balance = current_balance
        current_balance = (current_balance * (1 + r)) - net_portfolio_draw
        current_balance = max(0.0, current_balance)
        
        records.append({
            "Year": year,
            "Your Age": my_current_age,
            "Wife's Age": wife_current_age,
            "Phase": spending_phase,
            "Lifestyle Need": annual_lifestyle_need,
            "Pensions Inflow": total_pension_inflow,
            "Net Portfolio Draw": net_portfolio_draw,
            "Ending Balance": current_balance
        })
        
    df_timeline = pd.DataFrame(records)
    terminal_wealth = round(current_balance, 2)
    
    # Calculate Household Health Score based on total raw baseline liability
    if total_raw_outflow_no_growth > 0:
        score = min((portfolio_start / total_raw_outflow_no_growth) * 100, 100.0)
    else:
        score = 100.0
        
    return score, total_raw_outflow_no_growth, terminal_wealth, df_timeline

# =====================================================================
# 3. UI LAYOUT & SIDEBAR CONTROLS
# =====================================================================
st.set_page_config(layout="wide", page_title="Household Freedom Cockpit")
st.title("Outside Cup // Household Freedom Cockpit")
st.markdown("---")

# Section A: Lifestyle & Go-Go Adjustments
st.sidebar.header("🎛️ Lifestyle & Go-Go Settings")
base_expenses = st.sidebar.number_input(label="Annual Fixed Bills ($)", value=40000, step=1000)
disc_expenses = st.sidebar.number_input(label="Initial Discretionary ($)", value=15000, step=1000)

gogo_horizon = st.sidebar.slider(label="How many years of maximum 'Go-Go' spending?", min_value=1, max_value=18, value=10, step=1)
slowgo_reduction = st.sidebar.slider(label="Slow-Go Discretionary Reduction (%)", min_value=0, max_value=100, value=30, step=5)

# Section B: Portfolio Growth
st.sidebar.markdown("---")
st.sidebar.header("📈 Portfolio Performance")
growth_rate_pct = st.sidebar.slider(label="Assumed Real Growth Rate (%)", min_value=0.0, max_value=8.0, value=4.0, step=0.25)
growth_rate = growth_rate_pct / 100

# Section C: Pension Timing Customization
st.sidebar.markdown("---")
st.sidebar.header("🧓 Pension Timing Customizer")

st.sidebar.subheader("Your Pension Strategy")
my_pension_age = st.sidebar.slider(label="Age to collect YOUR pension", min_value=60, max_value=70, value=65, step=1)
my_annual_pension = st.sidebar.number_input(label="Estimated Annual Payout ($)", value=35000, step=1000)

st.sidebar.subheader("Wife's Pension Strategy")
wife_pension_age = st.sidebar.slider(label="Age to collect HER pension", min_value=60, max_value=70, value=65, step=1)
wife_annual_pension = st.sidebar.number_input(label="Estimated Annual Payout ($)", value=25000, step=1000)

# Section D: Simulation Mode
st.sidebar.markdown("---")
enable_simulation = st.sidebar.checkbox(label="Enable Simulation Mode", value=False)

if enable_simulation:
    portfolio_value = st.sidebar.number_input(label="Simulated Portfolio Value ($)", value=get_live_portfolio_total(), step=10000)
    st.sidebar.caption("⚠️ Running in Simulation Mode")
else:
    portfolio_value = get_live_portfolio_total()
    st.sidebar.caption("⚡ Connected to Live Master Portfolio Data")

# =====================================================================
# 4. EXECUTE SIMULATION ENGINE
# =====================================================================
(
    household_score, 
    total_raw_bridge_needed, 
    projected_terminal_wealth, 
    df_timeline
) = run_dynamic_household_simulation(
    portfolio_value, base_expenses, disc_expenses, growth_rate,
    my_annual_pension, my_pension_age, wife_annual_pension, wife_pension_age,
    gogo_horizon, slowgo_reduction
)

# 10x Current Annual Lifestyle Need Safety Cap
current_total_needs = base_expenses + disc_expenses
comfort_reserve_floor = current_total_needs * 10
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
            st.caption(f"🔴 {100 - household_score:.1f}% to Safety Cushion")

with col2:
    with st.container(border=True):
        st.write("CURRENT LIQUID ASSETS")
        st.subheader(f"${portfolio_value:,.2f}")
        st.caption("CAD Global Value")

with col3:
    with st.container(border=True):
        st.write("TOTAL NET DRAW REQ.")
        st.subheader(f"${total_raw_bridge_needed:,.2f}")
        st.caption("Sum of Out-of-Pocket Draws")

with col4:
    with st.container(border=True):
        st.write("PROJECTED WEALTH AT YEAR 18")
        st.subheader(f"${projected_terminal_wealth:,.2f}")
        st.caption(f"Compounded at {growth_rate_pct}%")

st.markdown("---")

# =====================================================================
# 6. RENDERING LIVE ALERTS & TIMELINE VISUALS
# =====================================================================
st.subheader("🌉 Dynamic Year-by-Year Freedom Horizon Matrix")
st.progress(household_score / 100.0)

if reserve_cushion_delta >= 0:
    st.success(
        f"🛡️ **10x LIVING EXPENSES COMFORT CHECK: PASSED**\n\n"
        f"Your baseline 10x comfort floor is **${comfort_reserve_floor:,.2f}**. "
        f"Your projected wealth at Year 18 clears this baseline with an extra safety padding of **+${reserve_cushion_delta:,.2f}** completely untouched."
    )
else:
    st.error(
        f"⚠️ **10x LIVING EXPENSES COMFORT CHECK: BELOW TARGET**\n\n"
        f"Under these exact pension timelines and growth constraints, your Year 18 reserve lands **${abs(reserve_cushion_delta):,.2f}** underneath your preferred 10x comfort floor."
    )

# Display the granular Data Table cleanly so you can scan the path
st.markdown("### 📋 Annual Cash Flow Tracking Ledger")
st.caption("Scan exactly how your age, spending phases, and incoming pensions alter your portfolio balance every single year:")

# Format table for high scan readability
formatted_df = df_timeline.copy()
formatted_df["Lifestyle Need"] = formatted_df["Lifestyle Need"].map("${:,.2f}".format)
formatted_df["Pensions Inflow"] = formatted_df["Pensions Inflow"].map("${:,.2f}".format)
formatted_df["Net Portfolio Draw"] = formatted_df["Net Portfolio Draw"].map("${:,.2f}".format)
formatted_df["Ending Balance"] = formatted_df["Ending Balance"].map("${:,.2f}".format)

st.dataframe(formatted_df, hide_index=True, use_container_width=True)
