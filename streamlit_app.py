import streamlit as st
import pandas as pd

# 1. PENSION & TAX ENGINE
def scale_cpp(base, age):
    if age == 65: return base
    return max(0.0, base * (1 - ((65 - age) * 12 * 0.006))) if age < 65 else base * (1 + ((age - 65) * 12 * 0.007))

def scale_oas(base, age):
    return 0.0 if age < 65 else (base if age == 65 else base * (1 + ((age - 65) * 12 * 0.006)))

# 2. FULL LIFETIME SIMULATION ENGINE
def run_lifetime_simulation(balances, base_bills, start_disc, growth_rate, my_cpp_65, my_cpp_age, my_oas_65, my_oas_age, wife_stop_work_age, wife_work_base, wife_work_start_age, wife_cpp_65, wife_cpp_age, wife_oas_65, wife_oas_age, gogo_years, slowgo_drop_pct, annual_savings, rrsp_tax_rate_pct, non_reg_tax_drag_pct, total_sim_years):
    my_start_age, wife_start_age = 57, 47
    n, r, t = balances["Non-Reg"] + balances["Crypto"], balances["RRSP"] + balances["Direct-Reg"], balances["TFSA"]
    records = []
    
    for year in range(1, total_sim_years + 1):
        my_age, wife_age = my_start_age + year - 1, wife_start_age + year - 1
        target = base_bills + (start_disc if year <= gogo_years else (start_disc * (1 - (slowgo_drop_pct / 100))))
        pens = (scale_cpp(my_cpp_65, my_cpp_age) if my_age >= my_cpp_age else 0) + (scale_oas(my_oas_65, my_oas_age) if my_age >= my_oas_age else 0) + (wife_work_base if wife_age >= wife_work_start_age else 0) + (scale_cpp(wife_cpp_65, wife_cpp_age) if wife_age >= wife_cpp_age else 0) + (scale_oas(wife_oas_65, wife_oas_age) if wife_age >= wife_oas_age else 0)
        
        n *= (1 + (growth_rate * (1 - (non_reg_tax_drag_pct / 100)))); r *= (1 + growth_rate); t *= (1 + growth_rate)
        
        if wife_age < wife_stop_work_age: n += annual_savings; status = "Working"
        else: n -= max(0, target - pens); status = "Drawing"
            
        records.append({"Year": year, "Age": my_age, "Pension": pens, "Non-Reg": n, "RRSP": r, "TFSA": t, "Total": n+r+t})
    return pd.DataFrame(records)

# 3. UI DASHBOARD
st.set_page_config(layout="wide")
st.title("Household Freedom Cockpit")

# State Initialization
if 'bal' not in st.session_state:
    st.session_state.bal = {"Non-Reg": 273030.44, "RRSP": 258250.91, "TFSA": 210667.74, "Direct-Reg": 49300.52, "Crypto": 4569.33}

with st.sidebar.form("update_form"):
    st.header("Update Portfolio")
    for k in st.session_state.bal:
        st.session_state.bal[k] = st.number_input(k, value=st.session_state.bal[k])
    if st.form_submit_button("Update"): st.rerun()

# Execute Simulation
df = run_lifetime_simulation(st.session_state.bal, 40000, 15000, 0.04, 3000, 65, 8916, 65, 65, 18000, 65, 12000, 65, 8916, 65, 10, 30, 15000, 15, 15, 38)

# Render Results
col1, col2 = st.columns(2)
col1.metric("TERMINAL WEALTH", f"${df['Total'].iloc[-1]:,.2f}")
st.dataframe(df, use_container_width=True)
