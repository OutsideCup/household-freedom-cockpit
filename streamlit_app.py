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
