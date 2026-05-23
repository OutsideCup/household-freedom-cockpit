import streamlit as st
import pandas as pd

# 1. PENSION CALCULATION ENGINE
def scale_cpp(base, age):
    if age == 65: return base
    return max(0.0, base * (1 - ((65 - age) * 12 * 0.006))) if age < 65 else base * (1 + ((age - 65) * 12 * 0.007))

def scale_oas(base, age):
    return 0.0 if age < 65 else (base if age == 65 else base * (1 + ((age - 65) * 12 * 0.006)))

# 2. UPDATED SIMULATION ENGINE
# UPDATE LINE 13 TO THIS:
def run_lifetime_simulation(bal, bills, disc, growth, my_cpp, my_a, my_oas, my_oas_a, w_stop, w_work, w_start, w_cpp, w_cpp_a, w_oas, w_oas_a, gogo, slowgo, sav, tx_r, tx_n, yrs):
    n, r, t = bal["Non-Reg"] + bal["Crypto"], bal["RRSP"] + bal["Direct-Reg"], bal["TFSA"]
    recs = []
    
    # We use these fixed placeholders for now, which you can swap for sidebar inputs later
    my_oas, my_oas_a = 8916, 65
    
    for y in range(1, yrs + 1):
        my_curr = 57 + y - 1
        w_curr = 47 + y - 1
        
        # Calculate pension inflow for this year
        pensions = 0
        if my_curr >= my_a: pensions += scale_cpp(my_cpp, my_a)
        if my_curr >= my_oas_a: pensions += scale_oas(my_oas, my_oas_a)
        if w_curr >= w_start: pensions += w_work
        
        # Apply growth
        n *= (1 + growth); r *= (1 + growth); t *= (1 + growth)
        
        # Logic: If working, save; if retired, use pensions to offset bills
        if w_curr < 65: 
            n += 15000 # Your existing savings logic
        else:
            n -= max(0, (bills + disc) - pensions)
            
        recs.append({"Year": y, "Pensions": round(pensions, 2), "Wealth": round(n + r + t, 2)})
        
    return pd.DataFrame(recs)

# 3. UI DASHBOARD
st.set_page_config(layout="wide")
st.title("Household Freedom Cockpit")

# Portfolio Initialization
if 'bal' not in st.session_state:
    st.session_state.bal = {"Non-Reg": 273030.44, "RRSP": 258250.91, "TFSA": 210667.74, "Direct-Reg": 49300.52, "Crypto": 4569.33}
    st.session_state.bal["Total"] = sum(st.session_state.bal.values())

with st.sidebar.form("portfolio_update"):
    st.header("1. Update Portfolio")
    inputs = {k: st.number_input(k, value=st.session_state.bal.get(k, 0.0)) for k in st.session_state.bal if k != "Total"}
    if st.form_submit_button("Update Balances"):
        inputs["Total"] = sum(inputs.values())
        st.session_state.bal = inputs

st.sidebar.markdown("---")
st.sidebar.header("2. Pension & Strategy Settings")
# Re-adding your granular controls
my_cpp = st.sidebar.number_input("Your CPP ($)", value=3000)
my_cpp_a = st.sidebar.slider("Your CPP Start Age", 60, 70, 65)
w_work = st.sidebar.number_input("Wife's Pension ($)", value=18000)
# (Add more as needed here, keeping it compact)

# 4. RUN & RENDER
# UPDATE LINE 68 IN streamlit_app.py TO THIS:
# Use this call at the bottom of your code
df = run_lifetime_simulation(
    st.session_state.bal, # 1: bal
    40000,                # 2: bills
    15000,                # 3: disc
    0.04,                 # 4: growth
    my_cpp,               # 5: my_cpp
    my_cpp_a,             # 6: my_a
    8916,                 # 7: my_oas
    65,                   # 8: my_oas_a
    65,                   # 9: w_stop
    w_work,               # 10: w_work
    65,                   # 11: w_start
    12000,                # 12: w_cpp
    65,                   # 13: w_cpp_a
    8916,                 # 14: w_oas
    65,                   # 15: w_oas_a
    10,                   # 16: gogo
    30,                   # 17: slowgo
    15000,                # 18: sav
    15,                   # 19: tx_r
    15,                   # 20: tx_n
    38                    # 21: yrs
)

st.metric("TERMINAL WEALTH", f"${df['Wealth'].iloc[-1]:,.2f}")
st.dataframe(df, use_container_width=True)
