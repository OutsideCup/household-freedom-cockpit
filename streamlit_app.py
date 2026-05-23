import streamlit as st
import pandas as pd

# 1. PENSION CALCULATION ENGINE
def scale_cpp(base, age):
    if age == 65: return base
    return max(0.0, base * (1 - ((65 - age) * 12 * 0.006))) if age < 65 else base * (1 + ((age - 65) * 12 * 0.007))

def scale_oas(base, age):
    return 0.0 if age < 65 else (base if age == 65 else base * (1 + ((age - 65) * 12 * 0.006)))

# 2. SIMULATION ENGINE
def run_lifetime_simulation(bal, bills, disc, growth, my_cpp, my_a, my_oas, my_oas_a, w_stop, w_work, w_start, w_cpp, w_cpp_a, w_oas, w_oas_a, gogo, slowgo, sav, tx_r, tx_n, yrs):
    n, r, t = bal["Non-Reg"] + bal["Crypto"], bal["RRSP"] + bal["Direct-Reg"], bal["TFSA"]
    recs = []
    for y in range(1, yrs + 1):
        my_curr, w_curr = 57 + y - 1, 47 + y - 1
        target = bills + (disc if y <= gogo else disc * (1 - (slowgo / 100)))
        pens = (scale_cpp(my_cpp, my_a) if my_curr >= my_a else 0) + (scale_oas(my_oas, my_oas_a) if my_curr >= my_oas_a else 0) + (w_work if w_curr >= w_start else 0) + (scale_cpp(w_cpp, w_cpp_a) if w_curr >= w_cpp_a else 0) + (scale_oas(w_oas, w_oas_a) if w_curr >= w_oas_a else 0)
        n *= (1 + (growth * (1 - tx_n / 100))); r *= (1 + growth); t *= (1 + growth)
        if w_curr < w_stop: n += sav
        else: n -= max(0, target - pens)
        recs.append({"Year": y, "Wealth": n + r + t})
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
df = run_lifetime_simulation(st.session_state.bal, 40000, 15000, 0.04, my_cpp, my_cpp_a, 8916, 65, 65, w_work, 65, 12000, 65, 8916, 65, 10, 30, 15000, 15, 15, 38)

st.metric("TERMINAL WEALTH", f"${df['Wealth'].iloc[-1]:,.2f}")
st.dataframe(df, use_container_width=True)
