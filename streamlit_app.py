import streamlit as st
import pandas as pd

def get_d(): return {"Non-Reg": 273030.44, "RRSP": 258250.91, "TFSA": 210667.74, "Direct-Reg": 49300.52, "Crypto": 4569.33}

def sim(bal, bills, disc, growth, m_cpp, m_age, m_oas, m_oas_age, w_stop, w_work, w_start, w_cpp, w_cpp_age, w_oas, w_oas_age, gogo, slowgo, sav, tx_r, tx_n, yrs):
    n, r, t = bal["Non-Reg"]+bal["Crypto"], bal["RRSP"]+bal["Direct-Reg"], bal["TFSA"]
    recs, draws, added = [], 0.0, 0.0
    for y in range(1, yrs+1):
        m_a, w_a = 57+y-1, 47+y-1
        p = (scale_cpp(m_cpp, m_age) if m_a>=m_age else 0)+(scale_oas(m_oas, m_oas_age) if m_a>=m_oas_age else 0)+(w_work if w_a>=w_start else 0)+(scale_cpp(w_cpp, w_cpp_age) if w_a>=w_cpp_age else 0)+(scale_oas(w_oas, w_oas_age) if w_a>=w_oas_age else 0)
        n*=(1+(growth*(1-(tx_n/100)))); r*=(1+growth); t*=(1+growth)
        if w_a < w_stop: n+=sav; added+=sav
        else:
            sh = max(0.0, (bills+(disc if y<=gogo else disc*(1-(slowgo/100))))-p); d = sh
            n_d = min(d, n); n-=n_d; d-=n_d
            if d > 0: r_d = min(d/(1-(tx_r/100)), r); r-=r_d; d-=(r_d*(1-(tx_r/100)))
            t-=min(d, t); draws+=sh
        recs.append({"Year": y, "Wealth": n+r+t})
    return min((sum(bal.values())/draws)*100, 100.0) if draws>0 else 100.0, added, round(recs[-1]["Wealth"], 2), pd.DataFrame(recs)

def scale_cpp(b, a):
    if a==65: return b
    return max(0.0, b*(1-((65-a)*12*0.006))) if a<65 else b*(1+((a-65)*12*0.007))

def scale_oas(b, a):
    return 0.0 if a<65 else (b if a==65 else b*(1+((a-65)*12*0.006)))

st.set_page_config(layout="wide"); st.title("Household Freedom")
if 'bal' not in st.session_state: st.session_state.bal = {**get_d(), "Total": sum(get_d().values())}
with st.sidebar.form("p"):
    b = {k: st.number_input(k, value=st.session_state.bal.get(k, get_d()[k])) for k in get_d()}
    if st.form_submit_button("Update"): st.session_state.bal = {**b, "Total": sum(b.values())}
sc, ad, tm, df = sim(st.session_state.bal, 40000, 15000, 0.04, 3000, 65, 8916, 65, 65, 18000, 65, 12000, 65, 8916, 65, 10, 30, 15000, 15, 15, 38)
c1, c2, c3, c4 = st.columns(4)
c1.metric("SCORE", f"{sc:.1f}%"); c2.metric("ASSETS", f"${st.session_state.bal['Total']:,.2f}"); c3.metric("SAVED", f"${ad:,.2f}"); c4.metric("WEALTH", f"${tm:,.2f}")
st.dataframe(df, use_container_width=True)
