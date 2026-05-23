import streamlit as st
import pandas as pd

# =====================================================================
# 1. INTEGRATION: MANUAL OVERRIDE ENGINE
# =====================================================================
def get_default_balances():
    return {
        "Non-Reg": 273030.44,
        "RRSP": 258250.91,
        "TFSA": 210667.74,
        "Direct-Reg": 49300.52,
        "Crypto": 4569.33
    }

# =====================================================================
# 2. CANADIAN PENSION & TAX ADJUSTMENT ENGINES
# =====================================================================
def scale_cpp(base_at_65, start_age):
    if start_age == 65: return base_at_65
    if start_age < 65:
        return max(0.0, base_at_65 * (1 - ((65 - start_age) * 12 * 0.006)))
    return base_at_65 * (1 + ((start_age - 65) * 12 * 0.007))

def scale_oas(base_at_65, start_age):
    if start_age < 65: return 0.0
    if start_age == 65: return base_at_65
    return base_at_65 * (1 + ((start_age - 65) * 12 * 0.006))

# =====================================================================
# 3. TAX-AWARE LIFETIME SIMULATION ENGINE
# =====================================================================
def run_lifetime_simulation(balances, base_bills, start_disc, gross_growth_rate,
    my_cpp_65, my_cpp_age, my_oas_65, my_oas_age,
    wife_stop_work_age, wife_work_base, wife_work_start_age, 
    wife_cpp_65, wife_cpp_age, wife_oas_65, wife_oas_age,
    gogo_years, slowgo_drop_pct, annual_surplus_savings,
    rrsp_tax_rate_pct, non_reg_tax_drag_pct, total_sim_years):
    
    my_start_age, wife_start_age = 57, 47
    non_reg = balances["Non-Reg"] + balances["Crypto"]
    rrsp = balances["RRSP"] + balances["Direct-Reg"]
    tfsa = balances["TFSA"]
    
    my_annual_cpp, my_annual_oas = scale_cpp(my_cpp_65, my_cpp_age), scale_oas(my_oas_65, my_oas_age)
    wife_annual_work, wife_annual_cpp, wife_annual_oas = wife_work_base, scale_cpp(wife_cpp_65, wife_cpp_age), scale_oas(wife_oas_65, wife_oas_age)
    
    non_reg_growth = gross_growth_rate * (1 - (non_reg_tax_drag_pct / 100))
    
    records, total_raw_draws_needed, total_raw_savings_added = [], 0.0, 0.0
    
    for year in range(1, total_sim_years + 1):
        my_age, wife_age = my_start_age + year - 1, wife_start_age + year - 1
        
        target = base_bills + (start_disc if year <= gogo_years else start_disc * (1 - (slowgo_drop_pct / 100)))
        
        pensions = (my_annual_cpp if my_age >= my_cpp_age else 0) + (my_annual_oas if my_age >= my_oas_age else 0) + \
                   (wife_annual_work if wife_age >= wife_work_start_age else 0) + (wife_annual_cpp if wife_age >= wife_cpp_age else 0) + \
                   (wife_annual_oas if wife_age >= wife_oas_age else 0)
        
        non_reg *= (1 + non_reg_growth)
        rrsp *= (1 + gross_growth_rate)
        tfsa *= (1 + gross_growth_rate)
        
        if wife_age < wife_stop_work_age:
            non_reg += annual_surplus_savings
            status, net_flow = "Working (Stacking)", annual_surplus_savings
            total_raw_savings_added += annual_surplus_savings
        else:
            shortfall = max(0.0, target - pensions)
            draw = shortfall
            
            non_reg_draw = min(draw, non_reg)
            non_reg -= non_reg_draw
            draw -= non_reg_draw
            
            if draw > 0 and rrsp > 0:
                gross_rrsp = min(draw / (1 - (rrsp_tax_rate_pct / 100)), rrsp)
                rrsp -= gross_rrsp
                draw -= (gross_rrsp * (1 - (rrsp_tax_rate_pct / 100)))
            
            tfsa -= min(draw, tfsa)
            status, net_flow = "Drawing Cash", -shortfall
            total_raw_draws_needed += shortfall
            
        records.append({"Year": year, "Status": status, "Net Need": target, "Pensions": pensions, "Net Flow": net_flow, "Non-Reg": non_reg, "RRSP": rrsp, "TFSA": tfsa, "Wealth": (non_reg + rrsp + tfsa)})
    
    # Simple, explicit logic for score
    if total_raw_draws_needed > 0:
        health = min((sum(balances.values()) / total_raw_draws_needed) * 100, 100.0)
    else:
        health = 100.0
        
    return health, total_raw_draws_needed, total_raw_savings_added, round(records[-1]["Wealth"], 2), pd.DataFrame(records)

# =====================================================================
# 4. STREAMLIT UI
# =====================================================================
st.set_page_config(layout="wide", page_title="Cockpit")
st.title("Household Freedom")

with st.sidebar.form("portfolio_form"):
    st.header("📈 Manual Portfolio Update")
    d = get_default_balances()
    b = {k: st.number_input(k, value=d[k]) for k in d}
    submitted = st.form_submit_button("Update Balances")
    balances = {**b, "Total": sum(b.values())} if submitted else {**d, "Total": sum(d.values())}

# ... (Keep your existing sidebar sliders here) ...

# =====================================================================
# 5. RENDER
# =====================================================================
# (Keep your rendering logic exactly as it was)
