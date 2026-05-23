import streamlit as st
import pandas as pd

def get_default_balances():
    return {"Non-Reg": 273030.44, "RRSP": 258250.91, "TFSA": 210667.74, "Direct-Reg": 49300.52, "Crypto": 4569.33}

def scale_cpp(b, a):
    if a == 65: return b
    if a < 65: return max(0.0, b * (1 - ((65 - a) * 12 * 0.006)))
    return b * (1 + ((a - 65) * 12 * 0.007))

def scale_oas(b, a):
    if a < 65: return 0.0
    if a == 65: return b
    return b * (1 + ((a - 65) * 12 * 0.006))

def run_lifetime_simulation(balances, base_bills, start_disc, growth, my_cpp, my_cpp_age, my_oas, my_oas_age, wife_stop, wife_work, wife_work_start, wife_cpp, wife_cpp_age, wife_oas, wife_oas_age, gogo, slowgo, savings, tax_rrsp, tax_nonreg, years):
    my_start, wife_start = 57, 47
    n_reg, rrsp, tfsa = balances["Non-Reg"] + balances["Crypto"], balances["RRSP"] + balances["Direct-Reg"], balances["TFSA"]
    cpp_my, oas_my = scale_cpp(my_cpp, my_cpp_age), scale_oas(my_oas, my_oas_age)
    work_wife, cpp_wife, oas_wife = wife_work, scale_cpp(wife_cpp, wife_cpp_age), scale_oas(wife_oas, wife_oas_age)
    n_reg_gr = growth * (1 - (tax_nonreg / 100))
    recs, draws, added = [], 0.0, 0.0
    for y in range(1, years + 1):
        my_age, wife_age = my_start + y - 1, wife_start + y - 1
        target = base_bills + (start_disc if y <= gogo else start_disc * (1 - (slowgo / 100)))
        pens = (cpp_my if my_age >= my_cpp_age else 0) + (oas_my if my_age >= my_oas_age else 0) + (work_wife if wife_age >= wife_work_start else 0) + (cpp_wife if wife_age >= wife_cpp_age else 0) + (oas_wife if wife_age >= wife_oas_age else 0)
        n_reg *= (1 + n_reg_gr); rrsp *= (1 + growth); tfsa *=
