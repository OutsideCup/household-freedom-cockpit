import streamlit as st
import pandas as pd

# 1. HELPER FUNCTIONS
def get_defaults():
    d = {"Non-Reg": 273030.44, "RRSP": 258250.91, "TFSA": 210667.74, "Direct-Reg": 49300.52, "Crypto": 4569.33}
    d["Total"] = sum(d.values())
    return d

def scale_cpp(base, age):
    if age == 65: return base
    return max(0.0, base * (1 - ((65 - age) * 12 * 0.006))) if age < 65 else base * (1 + ((age - 65) * 12 * 0.007))

def scale_oas(base, age):
    return 0.0 if age < 65 else (base if age == 65 else base * (1 + ((age - 65) * 12 * 0.006)))

# 2. SIMULATION ENGINE
def run_sim(bal, bills, disc, growth, tax_rrsp, tax_n, yrs, my_cpp, my_a, my_oas, my_oas_a, w_stop, w_work, w_start, w_cpp, w_cpp_a, w_oas, w_oas_a):
    n, r, t = bal["Non-Reg"] + bal["Crypto"], bal["RRSP"] + bal["Direct-Reg"], bal["TFSA"]
    recs = []
    for y in range(1, yrs + 1):
        my_a_curr, w_a_curr = 57 + y - 1, 47 + y - 1
        pens = (scale_cpp(my_cpp, my_a) if my_a_curr >= my_a else 0) + (scale_oas(my_oas, my_oas_a) if my_a_curr >= my_oas_a else 0) + (w_work if w_a_curr >= w_start else 0) + (scale_cpp(w_cpp, w_cpp_a) if w_a_curr >= w_cpp_a else 0) + (scale_oas(w_oas, w_oas_a) if w_a_curr >= w_oas_a else 0)
        n *= (1 + (growth * (1 -
