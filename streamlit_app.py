import streamlit as st
import pandas as pd
import os

# =====================================================================
# 1. INTEGRATION: EXPLICIT ACCOUNT TYPE BREAKDOWN
# =====================================================================
def get_account_balances():
    """Returns your exact real-world balances based on your inventory statements."""
    return {
        "Non-Reg": 273030.44,
        "RRSP": 258250.91,
        "TFSA": 210667.74,
        "Direct-Reg": 49300.52,
        "Crypto": 4569.33,
        "Total": 796576.07
    }

# =====================================================================
# 2. CANADIAN PENSION & TAX ADJUSTMENT ENGINES
# =====================================================================
def scale_cpp(base_at_65, start_age):
    if start_age == 65:
        return base_at_65
    elif start_age < 65:
        months_early = (65 - start_age) * 12
        return max(0.0, base_at_65 * (1 - (months_early * 0.006)))
    else:
        months_late = (start_age - 65) * 12
        return base_at_65 * (1 + (months_late * 0.007))

def scale_oas(base_at_65, start_age):
    if start_age < 65:
        return 0.0
    elif start_age == 65:
        return base_at_65
    else:
        months_late = (start_age - 65) * 12
        return base_at_65 * (1 + (months_late * 0.006))

# =====================================================================
# 3. TAX-AWARE ADVANCED SIMULATION ENGINE
# =====================================================================
def run_tax_aware_simulation(
    balances, base_bills, start_disc, gross_growth_rate,
    my_cpp_65, my_cpp_age, my_oas_65, my_oas_age,
    wife_stop_work_age, wife_work_base, wife_work_start_age, 
    wife_cpp_65, wife_cpp_age, wife_oas_65, wife_oas_age,
    gogo_years, slowgo_drop_pct, annual_surplus_savings,
    rrsp_tax_rate_pct, non_reg_tax_drag_pct
):
    my_start_age = 57
    wife_start_age = 47
    
    # Extract structural buckets
    non_reg = balances["Non-Reg"] + balances["Crypto"] # Liquid taxable mix
    rrsp = balances["RRSP"] + balances["Direct-Reg"]    # Deferred mix
    tfsa = balances["TFSA"]
    
    # Pre-calculate pension streams
    my_annual_cpp = scale_cpp(my_cpp_65, my_cpp_age)
    my_annual_oas = scale_oas(my_oas_65, my_oas_age)
    wife_annual_work = wife_work_base
    wife_annual_cpp = scale_cpp(wife_cpp_65, wife_cpp_age)
    wife_annual_oas = scale_oas(wife_oas_65, wife_oas_age)
    
    # Effective growth rates after internal annual tax friction
    rrsp_growth_rate = gross_growth_rate
    tfsa_growth_rate = gross_growth_rate
    non_reg_growth_rate = gross_growth_rate * (1 - (non_reg_tax_drag_pct / 100))
    
    records = []
    total_raw_draws_needed = 0.0
    total_raw_savings_added = 0.0
    
    for year in range(1, 19):
        my_age = my_start_age + year - 1
        wife_age = wife_start_age + year - 1
        
        # 1. Determine spending target for the year (After-Tax cash desired)
        if year <= gogo_years:
            target_after_tax_need = base_bills + start_disc
            phase_text = "Go-Go"
        else:
            target_after_tax_need = base_bills + (start_disc * (1 - (slowgo_drop_pct / 100)))
            phase_text = "Slow-Go"
            
        # 2. Gather incoming taxable pension cash flows
        in_my_cpp = my_annual_cpp if my_age >= my_cpp_age else 0.0
        in_my_oas = my_annual_oas if my_age >= my_oas_age else 0.0
        in_wife_work = wife_annual_work if wife_age >= wife_work_start_age else 0.0
        in_wife_cpp = wife_annual_cpp if wife_age >= wife_cpp_age else 0.0
        in_wife_oas = wife_annual_oas if wife_age >= wife_oas_age else 0.0
        
        total_pensions = in_my_cpp + in_my_oas + in_wife_work + in_wife_cpp + in_wife_oas
        
        # 3. Compound the distinct accounts internally first
        non_reg = non_reg * (1 + non_reg_growth_rate)
        rrsp = rrsp * (1 + rrsp_growth_rate)
        tfsa = tfsa * (1 + tfsa_growth_rate)
        
        wife_is_working = wife_age < wife_stop_work_age
        
        # 4. Execute cash flow draws or structural contributions
        if wife_is_working:
            # Active surplus added directly to your efficient Non-Reg account
            non_reg += annual_surplus_savings
            net_flow = annual_surplus_savings
            total_raw_savings_added += annual_surplus_savings
            status_text = "Working (Stacking Capital)"
        else:
            # Calculate the net cash shortfall after pension income
            net_cash_shortfall = max(0.0, target_after_tax_need - total_pensions)
            
            # Execute systematic, tax-efficient drawdown sequence
            draw_remaining = net_cash_shortfall
            
            # Sequence A: Draw from taxable Non-Reg first
            draw_from_non_reg = min(draw_remaining, non_reg)
            non_reg -= draw_from_non_reg
            draw_remaining -= draw_from_non_reg
            
            # Sequence B: Draw from RRSP next (Grossed up to cover the specified tax rate)
            if draw_remaining > 0 and rrsp > 0:
                tax_multiplier = 1 / (1 - (rrsp_tax_rate_pct / 100))
                gross_rrsp_draw_needed = draw_remaining * tax_multiplier
                
                actual_rrsp_draw = min(gross_rrsp_draw_needed, rrsp)
                rrsp -= actual_rrsp_draw
                # Net cash delivered to pocket after withholding tax
                net_rrsp_delivered = actual_rrsp_draw * (1 - (rrsp_tax_rate_pct / 100))
                draw_remaining -= net_rrsp_delivered
                
            # Sequence C: Draw from TFSA last as your ultimate tax-free defense shield
            draw_from_tfsa = min(draw_remaining, tfsa)
            tfsa -= draw_from_tfsa
            draw_remaining -= draw_from_tfsa
            
            net_flow = -net_cash_shortfall
            total_raw_draws_needed += net_cash_shortfall
            status_text = f"Drawing Cash ({phase_text})"
            
        total_combined_wealth = non_reg + rrsp + tfsa
        
        records.append({
            "Year": year,
            "Your Age": my_age,
            "Wife's Age": wife_age,
            "Status": status_text,
            "Target Net Need": target_after_tax_need,
            "Pension Inflow": total_pensions,
            "Net Portfolio Flow": net_flow,
            "Non-Reg Bal": non_reg,
            "RRSP Bal": rrsp,
            "TFSA Bal": tfsa,
            "Total Ending Wealth": total_combined_wealth
        })
        
    df_timeline = pd.DataFrame(records)
    terminal_wealth = round(total_combined_wealth, 2)
    health_score = min((balances["Total"] / total_raw_draws_needed) * 100, 100.0) if total_raw_draws_needed > 0 else 100.0
    
    return health_score, total_raw_draws_needed, total_raw_savings_added, terminal_wealth, df_timeline

# =====================================================================
# 4. STREAMLIT UI DESIGN & SIDEBAR
# =====================================================================
st.set_page_config(layout="wide", page_title="Household Freedom Cockpit")
st.title("Outside Cup // Household Freedom Cockpit")
st.markdown("---")

st.sidebar.header("🎛️ Lifestyle & Go-Go Controls")
base_expenses = st.sidebar.number_input(label="Annual Fixed Bills ($)", value=40000, step=1000)
disc_expenses = st.sidebar.number_input(label="Initial Discretionary ($)", value=15000, step=1000)
gogo_horizon = st.sidebar.slider(label="Go-Go Spending Horizon (Years)", min_value=1, max_value=18, value=10, step=1)
slowgo_reduction = st.sidebar.slider(label="Discretionary Drop in Slow-Go (%)", min_value=0, max_value=100, value=30, step=5)

st.sidebar.markdown("---")
st.sidebar.header("💰 Active Surplus Accumulation")
annual_savings = st.sidebar.number_input(label="Annual Portfolio Addition ($/yr)", value=15000, step=1000)

st.sidebar.markdown("---")
st.sidebar.header("📈 Growth Engine")
growth_rate_pct = st.sidebar.slider(label="Assumed Real Growth Rate (%)", min_value=0.0, max_value=8.0, value=4.0, step=0.25)
growth_rate = growth_rate_pct / 100

st.sidebar.markdown("---")
st.sidebar.header("🍁 Canadian Tax Friction Controls")
rrsp_tax_draw = st.sidebar.slider("Assumed RRSP Withholding Tax Rate (%)", 0, 40, 15, 5)
non_reg_tax_drag = st.sidebar.slider("Annual Non-Reg Capital Gains Tax Drag (%)", 0, 40, 15, 5)

st.sidebar.markdown("---")
st.sidebar.header("🇨🇦 Your Pension Settings")
my_cpp_65_est = st.sidebar.number_input("Your Age 65 CPP Estimate ($/yr)", value=3000, step=500)
my_cpp_start_age = st.sidebar.slider("Age to take your CPP", 60, 70, 65, 1)
my_oas_65_est = st.sidebar.number_input("Your Age 65 OAS Estimate ($/yr)", value=8916, step=100)
my_oas_start_age = st.sidebar.slider("Age to take your OAS", 65, 70, 65, 1)

st.sidebar.markdown("---")
st.sidebar.header("💃 Wife's Untangled Timeline")
wife_stop_work_age = st.sidebar.slider("Age she STOPS working", 47, 65, 65, 1)
wife_work_est = st.sidebar.number_input("Wife's Workplace Pension Base ($/yr)", value=18000, step=1000)
wife_work_start_age = st.sidebar.slider("Age she STARTS collecting workplace pension", 55, 65, 65, 1)

wife_cpp_65_est = st.sidebar.number_input("Wife's Age 65 CPP Estimate ($/yr)", value=12000, step=500)
wife_cpp_start_age = st.sidebar.slider("Age she takes her CPP", 60, 70, 65, 1)
wife_oas_65_est = st.sidebar.number_input("Wife's Age 65 OAS Estimate ($/yr)", value=8916, step=100)
wife_oas_start_age = st.sidebar.slider("Age she takes her OAS", 65, 70, 65, 1)

# Fetch static object map of account components
balances = get_account_balances()

# =====================================================================
# 5. RUN ENGINE LOGIC
# =====================================================================
(
    household_score,
    total_net_draws,
    total_added_savings,
    projected_terminal_wealth,
    df_timeline
) = run_tax_aware_simulation(
    balances, base_expenses, disc_expenses, growth_rate,
    my_cpp_65_est, my_cpp_start_age, my_oas_65_est, my_oas_start_age,
    wife_stop_work_age, wife_work_est, wife_work_start_age, 
    wife_cpp_65_est, wife_cpp_start_age, wife_oas_65_est, wife_oas_start_age,
    gogo_horizon, slowgo_reduction, annual_savings, rrsp_tax_draw, non_reg_tax_drag
)

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
        st.caption("Net-of-Tax Feasibility")
with col2:
    with st.container(border=True):
        st.write("CURRENT LIQUID ASSETS")
        st.subheader(f"${balances['Total']:,.2f}")
        st.caption("Aggregated Account Mix")
with col3:
    with st.container(border=True):
        st.write("TOTAL SURPLUS INVESTED")
        st.subheader(f"${total_added_savings:,.2f}")
        st.caption("Active Savings Stacked")
with col4:
    with st.container(border=True):
        st.write("TAX-AWARE WEALTH YEAR 18")
        st.subheader(f"${projected_terminal_wealth:,.2f}")
        st.caption(f"Net Ending Cushion @ {growth_rate_pct}%")

st.markdown("---")
st.subheader("🌉 Tax-Airtight Year-by-Year Freedom Horizon Matrix")
st.progress(household_score / 100.0)

if reserve_cushion_delta >= 0:
    st.success(f"🛡️ **10x COMFORT GUARDRAIL: PASSED** | Your net-of-tax Year 18 balance maintains a surplus of **+${reserve_cushion_delta:,.2f}** over your strict ${comfort_reserve_floor:,.2f} baseline floor.")
else:
    st.error(f"⚠️ **10x COMFORT GUARDRAIL: VIOLATED** | Tax friction and early draws pull your Year 18 net wealth down to **${abs(reserve_cushion_delta):,.2f}** below your safety threshold.")

st.markdown("### 📋 Granular Bucket-by-Bucket Ledger")
st.caption("Watch how the individual account balances compound independently and draw down using a tax-optimized sequence:")

formatted_df = df_timeline.copy()
for col in ["Target Net Need", "Pension Inflow", "Net Portfolio Flow", "Non-Reg Bal", "RRSP Bal", "TFSA Bal", "Total Ending Wealth"]:
    if col == "Net Portfolio Flow":
        formatted_df[col] = formatted_df[col].map(lambda x: f"${x:,.2f}" if x >= 0 else f"-${abs(x):,.2f}")
    else:
        formatted_df[col] = formatted_df[col].map("${:,.2f}".format)
        
st.dataframe(formatted_df, hide_index=True, use_container_width=True)
