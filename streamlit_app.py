import streamlit as st
import pandas as pd

# 1. Setup Defaults
def get_defaults():
    return {"Non-Reg": 273030.44, "RRSP": 258250.91, "TFSA": 210667.74, "Direct-Reg": 49300.52, "Crypto": 4569.33}
    
def scale_cpp(base, age):
    if age == 65: return base
    if age < 65: return max(0.0, base * (1 - ((65 - age) * 12 * 0.006)))
    return base * (1 + ((age - 65) * 12 * 0.007))

def scale_oas(base, age):
    if age < 65: return 0.0
    if age == 65: return base
    return base * (1 + ((age - 65) * 12 * 0.006))
# 2. Simulation Logic
def run_sim(bal, bills, disc, growth, yrs):
    n, r, t = bal["Non-Reg"] + bal["Crypto"], bal["RRSP"] + bal["Direct-Reg"], bal["TFSA"]
    recs = []
    total_added = 0.0
    for y in range(1, yrs + 1):
        # Apply growth
        n *= (1 + 0.04); r *= (1 + 0.04); t *= (1 + 0.04)
        # Simple Logic: Add savings
        n += 15000
        total_added += 15000
        recs.append({"Year": y, "Non-Reg": round(n, 2), "RRSP": round(r, 2), "TFSA": round(t, 2), "Total Wealth": round(n+r+t, 2)})
    return total_added, round(recs[-1]["Total Wealth"], 2), pd.DataFrame(recs)

# 3. Render Dashboard
st.set_page_config(layout="wide")
st.title("Household Freedom")

if 'bal' not in st.session_state:
    st.session_state.bal = {**get_defaults(), "Total": sum(get_defaults().values())}

with st.sidebar.form("update_form"):
    st.header("Update Balances")
    b = {k: st.number_input(k, value=st.session_state.bal.get(k, get_defaults()[k])) for k in get_defaults()}
    if st.form_submit_button("Update"):
        st.session_state.bal = {**b, "Total": sum(b.values())}

added, term, df = run_sim(st.session_state.bal, 40000, 15000, 0.04, 38)

c1, c2, c3 = st.columns(3)
c1.metric("TOTAL ASSETS", f"${st.session_state.bal['Total']:,.2f}")
c2.metric("TOTAL SAVED", f"${added:,.2f}")
c3.metric("TERMINAL WEALTH", f"${term:,.2f}")

st.subheader("Lifetime Projection")
st.dataframe(df, use_container_width=True)
