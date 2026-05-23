import streamlit as st
import pandas as pd

# Define helpers
def get_defaults():
    return {"Non-Reg": 273030.44, "RRSP": 258250.91, "TFSA": 210667.74, "Direct-Reg": 49300.52, "Crypto": 4569.33}

def scale_cpp(b, a):
    if a == 65: return b
    if a < 65: return max(0.0, b * (1 - ((65 - a) * 12 * 0.006)))
    return b * (1 + ((a - 65) * 12 * 0.007))

def scale_oas(b, a):
    if a < 65: return 0.0
    if a == 65: return b
    return b * (1 + ((a - 65) * 12 * 0.006))

# Main logic
def run_sim(bal, bills, disc, growth, m_cpp, m_age, m_oas, m_oas_age, w_stop, w_work, w_start, w_cpp, w_cpp_age, w_oas, w_oas_age, gogo, slowgo, sav, tax_r, tax_n, yrs):
    n_reg = bal["Non-Reg"] + bal["Crypto"]
    rrsp = bal["RRSP"] + bal["Direct-Reg"]
    tfsa = bal["TFSA"]
    
    # Calculate pensions
    cpp_m = scale_cpp(m_cpp, m_age)
    oas_m = scale_oas(m_oas, m_oas_age)
    cpp_w = scale_cpp(w_cpp, w_cpp_age)
    oas_w = scale_oas(w_oas, w_oas_age)
    
    recs = []
    draws_needed = 0.0
    total_added = 0.0
    
    for y in range(1, yrs + 1):
        my_a = 57 + y - 1
        w_a = 47 + y - 1
        
        target = bills + (disc if y <= gogo else disc * (1 - (slowgo / 100)))
        pens = (cpp_m if my_a >= m_age else 0) + (oas_m if my_a >= m_oas_age else 0) + (w_work if w_a >= w_start else 0) + (cpp_w if w_a >= w_cpp_age else 0) + (oas_w if w_a >= w_oas_age else 0)
        
        # Grow
        n_reg *= (1 + (growth * (1 - (tax_n / 100))))
        rrsp *= (1 + growth)
        tfsa *= (1 + growth)
        
        if w_a < w_stop:
            n_reg += sav
            total_added += sav
            status = "Working"
        else:
            short = max(0.0, target - pens)
            draw = short
            
            # Draw
            n_d = min(draw, n_reg)
            n_reg -= n_d
            draw -= n_d
            
            if draw > 0:
                r_d = min(draw / (1 - (tax_r / 100)), rrsp)
                rrsp -= r_d
                draw -= (r_d * (1 - (tax_r / 100)))
            
            tfsa -= min(draw, tfsa)
            draws_needed += short
            status = "Drawing"
            
        recs.append({"Year": y, "Wealth": (n_reg + rrsp + tfsa)})
        
    score = min((sum(bal.values()) / draws_needed) * 100, 100.0) if draws_needed > 0 else 100.0
    return score, total_added, round(recs[-
