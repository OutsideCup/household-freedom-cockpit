import streamlit as st
import pandas as pd
import os

# =====================================================================
# 1. INTEGRATION: CONNECT TO YOUR MASTER PORTFOLIO BACKEND
# =====================================================================
def get_live_portfolio_total():
    return 796576.07  # Matches your current master ledger total perfectly

# =====================================================================
# 2. CANADIAN PENSION ADJUSTMENT ENGINES
# =====================================================================
def scale_cpp(base_at_65, start_age):
    """Applies official CRA adjustments: -0.6%/mo before 65, +0.7%/mo after 65."""
    if start_age == 65:
        return base_at_65
    elif start_age < 65:
        months_early = (65 - start_age) * 12
        reduction_pct = months_early * 0.006  # 0.6% per month
        return max(0.0, base_at_65 * (1 - reduction_pct))
    else:
        months_late = (start_age - 65) * 12
        bonus_pct = months_late * 0.007  # 0.7% per month
        return base_at_65 * (1 + bonus_pct)

def scale_oas(base_at_65, start_age):
    """Applies official CRA adjustments: No collection before 65, +0.6%/mo after 65."""
    if start_age < 65:
        return 0.0  # Cannot collect OAS before 65
    elif start_age == 65:
        return base_at_65
    else:
        months_late = (start_age - 65) * 12
        bonus_pct = months_late * 0.006  # 0.6% per month
        return base_at_65 * (1 + bonus_pct)

# =====================================================================
# 3. ADVANCED YEAR-BY-YEAR FREEDOM SIMULATOR
# =====================================================================
def run_granular_bridge_simulation(
    portfolio_start, base_bills, start_disc, growth_rate,
    my_cpp_65, my_cpp_age, my_oas_65, my_oas_age,
    wife_work_base, wife_work_age, wife_cpp_65, wife_cpp_age, wife_oas_65, wife_oas_age,
    gogo_years, slowgo_drop_pct
):
    # Current Ages in 2026
    my_start_age = 57
    wife_start_age = 47
    
    # Calculate scaled values for life based on chosen start ages
    my_annual_cpp = scale_cpp(my_cpp_65, my_cpp_age)
    my_annual_oas = scale_oas(my_oas_65, my_oas_age)
    
    wife_annual_work = wife_work_base  # Simplified fixed base for work pension
    wife_annual_cpp = scale_cpp(wife_cpp_65, wife_cpp_age)
    wife_annual_oas = scale_oas(wife_oas_65, wife_oas_age)
    
    records = []
    current_balance = portfolio_start
    total_raw_draws = 0.0
    
    # Simulate 18 years out to clear the primary horizon
    for year in range(1, 19):
        my_age = my_start_age + year - 1
        wife_age = wife_start_age + year - 1
        
        # Spending Phase Logic
        if year <= gogo_years:
            current_disc = start_disc
            phase_text = "Go-Go"
        else:
            current_disc = start_disc * (1 - (slowgo_drop_pct / 100))
            phase_text = "Slow-Go"
            
        target_lifestyle_need = base_bills + current_disc
        
        # Calculate Active Inflows this specific year
        in_my_cpp = my_annual_cpp if my_age >= my_cpp_age else 0.0
        in_my_oas = my_annual_oas if my_age >= my_oas_age else 0.0
        
        in_wife_work = wife_annual_work if wife_age >= wife_work_age else 0.0
        in_wife_cpp = wife_annual_cpp if wife_age >= wife_cpp_age else 0.0
        in_wife_oas = wife_annual_oas if wife_age >= wife_oas_age else 0.0
        
        total_pensions_this_year = in_my_cpp + in_my_oas + in_wife_work + in_wife_cpp + in_wife_oas
        
        # Determine drawdown requirement
        net_portfolio_draw = max(0.0, target_lifestyle_need - total_pensions_this_year)
        total_raw_draws += net_portfolio_draw
        
        # Compound portfolio
        current_balance = (current_balance * (1 + growth_rate)) - net_portfolio_draw
        current_balance = max(0.0, current_balance)
        
        records.append({
            "Year": year,
            "Your Age": my_age,
            "Wife's Age": wife_age,
            "Spending Phase": phase_text,
            "Target Lifestyle": target_lifestyle_need,
            "Pension Inflow": total_pensions_this_year,
            "Net Portfolio Draw": net_portfolio_draw,
            "Ending Wealth": current_balance
        })
        
    df_timeline = pd.DataFrame(records)
    terminal_wealth = round(current_balance, 2)
    health_score = min((portfolio_start / total_raw_draws) * 100, 100.0) if total_raw_draws > 0 else 100.0
    
    return health_score, total_raw_draws, terminal_wealth, df_timeline, my_annual_cpp, my_annual_oas, wife_annual_cpp, wife_annual_oas

# =====================================================================
# 4. STREAMLIT UI DESIGN & SIDEBAR
# =====================================================================
st.set_page_config(layout="wide", page_title="Household Freedom Cockpit")
st.title("Household Freedom")
st.markdown("---")

# Sidebar Column 1: Expenses & Growth
st.sidebar.header("🎛️ Lifestyle & Go-Go Controls")
base_expenses = st.sidebar.number_input(label="Annual Fixed Bills ($)", value=40000, step=1000)
disc_expenses = st.sidebar.number_input(label="Initial Discretionary ($)", value=15000, step=1000)
gogo_horizon = st.sidebar.slider(label="Go-Go Spending Horizon (Years)", min_value=1, max_value=18, value=10, step=1)
slowgo_reduction = st.sidebar.slider(label="Discretionary Drop in Slow-Go (%)", min_value=0, max_value=100, value=30, step=5)

st.sidebar.markdown("---")
st.sidebar.header("📈 Growth Engine")
growth_rate_pct = st.sidebar.slider(label="Assumed Real Growth Rate (%)", min_value=0.0, max_value=8.0, value=4.0, step=0.25)
growth_rate = growth_rate_pct / 100

# Sidebar Column 2: Granular Canadian Pensions
st.sidebar.markdown("---")
st.sidebar.header("🇨🇦 Your Pension Settings")
my_cpp_65_est = st.sidebar.number_input("Your Age 65 CPP Estimate ($/yr)", value=3000, step=500)
my_cpp_start_age = st.sidebar.slider("Age to take your CPP", 60, 70, 65, 1)
my_oas_65_est = st.sidebar.number_input("Your Age 65 OAS Estimate ($/yr)", value=8916, step=100)
my_oas_start_age = st.sidebar.slider("Age to take your OAS", 65, 70, 65, 1)

st.sidebar.markdown("---")
st.sidebar.header("💃 Wife's Pension Settings")
wife_work_est = st.sidebar.number_input("Wife's Workplace Pension ($/yr)", value=18000, step=1000)
wife_work_start_age = st.sidebar.slider("Age she stops working / takes pension", 47, 65, 65, 1)

wife_cpp_65_est = st.sidebar.number_input("Wife's Age 65 CPP Estimate ($/yr)", value=12000, step=500)
wife_cpp_start_age = st.sidebar.slider("Age she takes her CPP", 60, 70, 65, 1)
wife_oas_65_est = st.sidebar.number_input("Wife's Age 65 OAS Estimate ($/yr)", value=8916, step=100)
wife_oas_start_age = st.sidebar.slider("Age she takes her OAS", 65, 70, 65, 1)

# Execution Values
portfolio_value = get_live_portfolio_total()

# =====================================================================
# 5. RUN ENGINE LOGIC
# =====================================================================
(
    household_score,
    total_net_draws,
    projected_terminal_wealth,
    df_timeline,
    calculated_my_cpp,
    calculated_my_oas,
    calculated_wife_cpp,
    calculated_wife_oas
) = run_granular_bridge_simulation(
    portfolio_value, base_expenses, disc_expenses, growth_rate,
    my_cpp_65_est, my_cpp_start_age, my_oas_65_est, my_oas_start_age,
    wife_work_est, wife_work_start_age, wife_cpp_65_est, wife_cpp_start_age, wife_oas_65_est, wife_oas_start_age,
    gogo_horizon, slowgo_reduction
)

# 10x Guardrail calculation
comfort_reserve_floor = (base_expenses + disc_expenses) * 10
reserve_cushion_delta = projected_terminal_wealth - comfort_reserve_floor

# =====================================================================
# 6. UI RENDERING
# =====================================================================
col1, col2, col3, col4 = st.columns(4)
with col1:
    with st.container(border=True):
        st.write("HOUSEHOLD HEALTH SCORE")
        st.subheader(f"{household_score:.1f}%")
        st.caption("Bridge Feasibility Ratio")
with col2:
    with st.container(border=True):
        st.write("CURRENT LIQUID ASSETS")
        st.subheader(f"${portfolio_value:,.2f}")
        st.caption("Master Balance Baseline")
with col3:
    with st.container(border=True):
        st.write("TOTAL OUT-OF-POCKET DRAWS")
        st.subheader(f"${total_net_draws:,.2f}")
        st.caption("Net Capital Consumed")
with col4:
    with st.container(border=True):
        st.write("PROJECTED WEALTH AT YEAR 18")
        st.subheader(f"${projected_terminal_wealth:,.2f}")
        st.caption(f"Ending Cushion @ {growth_rate_pct}%")

st.markdown("---")
st.subheader("🌉 Dynamic Year-by-Year Freedom Horizon Matrix")
st.progress(household_score / 100.0)

if reserve_cushion_delta >= 0:
    st.success(f"🛡️ **10x COMFORT GUARDRAIL: PASSED** | Your Year 18 balance maintains a surplus of **+${reserve_cushion_delta:,.2f}** over your strict ${comfort_reserve_floor:,.2f} reserve threshold.")
else:
    st.error(f"⚠️ **10x COMFORT GUARDRAIL: VIOLATED** | Early exit conditions draw down your Year 18 wealth to **${abs(reserve_cushion_delta):,.2f}** below your preferred ${comfort_reserve_floor:,.2f} safety floor.")

# Show Scaled Estimates Box
with st.expander("🔍 View Live Scaled Payout Calculations (Based on Selected Ages)"):
    st.markdown(f"* **Your Calculated CPP Payout:** `${calculated_my_cpp:,.2f}/yr` (Age {my_cpp_start_age})")
    st.markdown(f"* **Your Calculated OAS Payout:** `${calculated_my_oas:,.2f}/yr` (Age {my_oas_start_age})")
    st.markdown(f"---")
    st.markdown(f"* **Wife's Workplace Pension Payout:** `${wife_work_est:,.2f}/yr` (Starts Age {wife_work_start_age})")
    st.markdown(f"* **Wife's Calculated CPP Payout:** `${calculated_wife_cpp:,.2f}/yr` (Age {wife_cpp_start_age})")
    st.markdown(f"* **Wife's Calculated OAS Payout:** `${calculated_wife_oas:,.2f}/yr` (Age {wife_oas_start_age})")

st.markdown("### 📋 Annual Cash Flow Tracking Ledger")
formatted_df = df_timeline.copy()
for col in ["Target Lifestyle", "Pension Inflow", "Net Portfolio Draw", "Ending Wealth"]:
    formatted_df[col] = formatted_df[col].map("${:,.2f}".format)
st.dataframe(formatted_df, hide_index=True, use_container_width=True)
