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
    elif start_age < 65:
        months_early = (65 - start_age) * 12
        return max(0.0, base_at_65 * (1 - (months_early * 0.006)))
    else:
        months_late = (start_age - 65) * 12
        return base_at_65 * (1 + (months_late * 0.007))

def scale_oas(base_at_65, start_age):
    if start_age < 65: return 0.0
    elif start_age == 65: return base_at_65
    else:
        months_late = (start_age - 65) * 12
        return base_at_65 * (1 + (months_late * 0.006))

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
