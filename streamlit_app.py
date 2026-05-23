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
    
    rrsp_growth_rate, tfsa_growth_rate = gross_growth_rate, gross_growth_rate
    non_reg_growth_rate = gross_growth_rate * (1 - (non_reg_tax_drag_pct / 100))
    
    records, total_raw_draws_needed, total_raw_savings_added = [], 0.0, 0.0
    
    for year in range(1, total_sim_years + 1):
        my_age, wife_age = my_start_age + year - 1, wife_start_age + year - 1
        target_after_tax_need = base_bills + (start_disc if year <= gogo_years else start_disc * (1 - (slowgo_drop_pct / 100)))
        
        total_pensions = (my_annual_cpp if my_age >= my_cpp_age else 0) + (my_annual_oas if my_age >= my_oas_age else 0) + \
                         (wife_annual_work if wife_age >= wife_work_start_age else 0) + (wife_annual_cpp if wife_age >= wife_cpp_age else 0) + \
                         (wife_annual_oas if wife_age >= wife_oas_age else 0)
        
        non_reg, rrsp, tfsa = non_reg * (1 + non_reg_growth_rate), rrsp * (1 + rrsp_growth_rate), tfsa * (1 + tfsa_growth_rate)
        
        if wife_age < wife_stop_work_age:
            non_reg += annual_surplus_savings
            net_flow, status_text = annual_surplus_savings, "Working (Stacking Capital)"
            total_raw_savings_added += annual_surplus_savings
        else:
            net_cash_shortfall = max(0.0, target_after_tax_need - total_pensions)
            draw_rem = net_cash_shortfall
            draw_non_reg = min(draw_rem, non_reg)
            non_reg -= draw_non_reg
            draw_rem -= draw_non_reg
            if draw_rem > 0 and rrsp > 0:
                gross_rrsp = min(draw_rem * (1 / (1 - (rrsp_tax_rate_pct / 100))), rrsp)
                rrsp -= gross_rrsp
                draw_rem -= (gross_rrsp * (1 - (rrsp_tax_rate_pct / 100)))
            tfsa -= min(draw_rem, tfsa)
            net_flow, status_text = -net_cash_shortfall, "Drawing Cash"
            total_raw_draws_needed += net_cash_shortfall
        
        records.append({"Year": year, "Your Age": my_age, "Wife's Age": wife_age, "Status": status_text, "Target Net Need": target_after_tax_need, "Pension Inflow": total_pensions, "Net Portfolio Flow": net_flow, "Non-Reg Bal": non_reg, "RRSP Bal": rrsp, "TFSA Bal": tfsa, "Total Ending Wealth": (non_reg + rrsp + tfsa)})
    
    return min((sum(balances.values()) / total_raw_draws_needed) * 100, 100.0) if total_raw_
