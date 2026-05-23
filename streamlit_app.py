import streamlit as st
import pandas as pd

def get_default_balances():
    return {"Non-Reg": 273030.44, "RRSP": 258250.91, "TFSA": 210667.74, "Direct-Reg": 49300.52, "Crypto": 4569.33}

def scale_cpp(base, age):
    if age == 65: return base
    if age < 65: return max(0.0, base * (1 - ((65 - age) * 12 * 0.006)))
    return base * (1 + ((age - 65) * 12 * 0.007))

def scale_oas(base, age):
    if age < 65: return 0.0
    if age == 65: return base
    return base * (1 + ((age - 65) * 12 * 0.006))

def run_lifetime_simulation(balances, base_bills, start_disc, gross_growth_rate, my_cpp_65, my_cpp_age, my_oas_65, my_oas_age, wife_stop_work_age, wife_work_base, wife_work_start_age, wife_cpp_65, wife_cpp_age, wife_oas_65, wife_oas_age, gogo_years, slowgo_drop_pct, annual_surplus_savings, rrsp_tax_rate_pct, non_reg_tax_drag_pct, total_sim_years):
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
        pensions = (my_annual_cpp
