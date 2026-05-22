import streamlit as st
import pandas as pd

# =====================================================================
# 1. CORE MATHEMATICAL ENGINES
# =====================================================================
def calculate_perpetual_freedom_score(portfolio_value, base_expenses, disc_expenses, swr=0.035):
    """Calculates traditional freedom score based on SWR."""
    safe_annual_income = portfolio_value * swr
    if safe_annual_income < base_expenses:
        score = (safe_annual_income / base_expenses) * 50
    else:
        base_score = 50
        if disc_expenses > 0:
            disc_coverage = ((safe_annual_income - base_expenses) / disc_expenses)
            score = base_score + (min(disc_coverage, 1.0) * 50)
        else:
            score = 100.0
    return round(score, 1), safe_annual_income

def calculate_household_bridge(portfolio_value, total_annual_needs, y_me, y_wife, p_me, p_wife):
    """Calculates time-horizon escrow required to bridge to pensions."""
    phase_1_duration = y_me
    phase_2_duration = max(0, y_wife - y_me)
    p1_total_cost = phase_1_duration * total_annual_needs
    p2_annual_needs = max(0, total_annual_needs - p_me)
    p2_total_cost = phase_2_duration * p2_annual_needs
    total_bridge_needed = p1_total_cost + p2_total_cost
    if total_bridge_needed > 0:
        score = min((portfolio_value / total_bridge_needed) * 100, 100.0)
    else:
        score = 100.0
    return (round(score, 1), total_bridge_needed, p1_total_cost, p2_total_cost, phase_1_duration, phase_2_duration, p2_annual_needs)

# =====================================================================
# 2. UI LAYOUT & CONTROL
