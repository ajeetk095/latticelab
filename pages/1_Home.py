import streamlit as st
from utils import ui, pricing as P

ui.hero("🌳 LatticeLab", ui.TAGLINE,
        '<p style="font-size:.9rem;opacity:.8">Based on MScFE 620 Group Work Project #1 (Group 9450): '
        + ui.PROJECT_TITLE + "</p>")

c = st.columns(4)
if c[0].button("🧪 Run Simulation", use_container_width=True, type="primary"): st.switch_page("pages/2_Live_Simulation.py")
if c[1].button("📄 View Report", use_container_width=True): st.switch_page("pages/6_Research_Report.py")
if c[2].button("🎞️ View Presentation", use_container_width=True): st.switch_page("pages/7_Presentation.py")
if c[3].button("👤 Connect With Developer", use_container_width=True): st.switch_page("pages/9_Contact.py")

st.subheader("Headline results (S₀=K=100, r=5%, σ=20%, T=0.25, N=100)")
S0, K, r, sg, T, N = 100, 100, .05, .20, .25, 100
call, put = P.binomial(S0, K, r, sg, T, N, "call"), P.binomial(S0, K, r, sg, T, N, "put")
g = P.greeks(S0, K, r, sg, T, N, "call")
bs = P.black_scholes(S0, K, r, sg, T, "call")
pc = P.parity_check(S0, K, r, sg, T, N)
k = st.columns(5)
ui.kpi(k[0], "European call", f"{call:.4f}", "CRR binomial")
ui.kpi(k[1], "European put", f"{put:.4f}", "CRR binomial")
ui.kpi(k[2], "Call delta", f"{g['delta']:.4f}", "finite difference")
ui.kpi(k[3], "Error vs Black–Scholes", f"{abs(call - bs):.1e}", f"BS = {bs:.4f}")
ui.kpi(k[4], "Parity residual", f"{abs(pc['residual']):.0e}", "C − P − (S₀−Ke⁻ʳᵀ)")
st.caption("This is a pricing project, not a trained ML model – there is no dataset, so accuracy/F1/RMSE do not apply. "
           "Pricing-quality metrics are shown instead.")

st.subheader("Why this matters")
a = st.columns(3)
ui.card(a[0], "💸 Pricing without formulas", "Trees price options that Black–Scholes cannot – early exercise (American) and path-dependent payoffs.")
ui.card(a[1], "🛡️ Risk management", "Greeks and delta-hedging show how traders neutralise exposure and what risk remains.")
ui.card(a[2], "🔍 Explainable", "Exact Shapley attribution tells you <i>which input</i> moved the price and by how much.")

st.subheader("Research objective")
st.markdown("""Implement and compare **binomial and trinomial lattice models** for European and American options,
verify **put–call parity**, estimate **Delta/Vega**, simulate **dynamic delta hedging**, and price an **Asian option** – then
make all of it interactive.""")
ui.disclaimer()
