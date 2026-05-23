# =====================================================================
# 1. CORE MATHEMATICAL ENGINES (Updated for multi-pension streams)
# =====================================================================
def calculate_household_bridge(portfolio_value, total_annual_needs, y_me, y_wife, p_me, p_wife, cpp, oas, wife_work_pension):
    phase_1_duration = y_me
    phase_2_duration = max(0, y_wife - y_me)
    
    # Phase 1: Only savings (no pensions active yet)
    p1_total_cost = phase_1_duration * total_annual_needs
    
    # Phase 2: Savings - (Your Pensions + Wife's Pensions)
    # Deducting all income sources from annual needs
    total_annual_income = p_me + cpp + oas + wife_work_pension
    p2_annual_needs = max(0, total_annual_needs - total_annual_income)
    p2_total_cost = phase_2_duration * p2_annual_needs
    
    total_bridge_needed = p1_total_cost + p2_total_cost
    score = min((portfolio_value / total_bridge_needed) * 100, 100.0) if total_bridge_needed > 0 else 100.0
    
    return (round(score, 1), total_bridge_needed, p1_total_cost, p2_total_cost, phase_1_duration, phase_2_duration, p2_annual_needs)

# =====================================================================
# 2. UI LAYOUT & SIDEBAR (Add these to your existing sidebar)
# =====================================================================
st.sidebar.markdown("---")
st.sidebar.header("🇨🇦 Pension & Benefit Settings")

# Existing
p_me = st.sidebar.number_input("My Work Pension ($)", value=35000, step=1000)
p_wife_work = st.sidebar.number_input("Wife's Work Pension ($)", value=0, step=1000)

# New Government Benefits
cpp = st.sidebar.number_input("Annual CPP ($)", value=10000, step=500)
oas = st.sidebar.number_input("Annual OAS ($)", value=8000, step=500)

# Pass these new variables into your existing 'calculate_household_bridge' function call
