from pathlib import Path
import streamlit as st
from utils import ui

ui.hero("📄 Research Report", "Group 9450 – MScFE 620 Derivative Pricing, Group Work Project #1.")
pdf = ui.ROOT / "reports" / "GPW1_9450_Report.pdf"
c = st.columns([1, 1, 2])
c[0].download_button("⬇️ Download report (PDF)", pdf.read_bytes(), pdf.name, "application/pdf", use_container_width=True)
brief = ui.ROOT / "documentation" / "Assignment_Brief.pdf"
c[1].download_button("⬇️ Assignment brief", brief.read_bytes(), brief.name, "application/pdf", use_container_width=True)
t1, t2, t3 = st.tabs(["Summary", "Conclusions & recommendations", "Full report"])
with t1:
    st.markdown("""**Scope.** European and American options priced with CRR binomial and Boyle trinomial trees; put–call parity checks;
Delta and Vega; dynamic delta hedging; and an Asian option.

**Reference run** (S₀=K=100, r=5 %, σ=20 %, T=0.25, N=100): European call **4.6050**, put **3.3628**; Delta call **0.5693**, put **−0.4307**; Vega ≈ **19.62** per 1.00 of volatility (0.196 per vol-point).
American calls for K = 90…110: 11.67, 7.72, 4.61, 2.49, 1.19. American puts: 0.56, 1.58, 3.47, 6.43, 10.33.""")
with t2:
    st.markdown("""**Conclusions**
- Lattice prices converge to Black–Scholes as N grows (binomial N=100 error ≈ 0.01).
- European put–call parity holds to machine precision; for American options only inequality bounds apply.
- American puts carry an early-exercise premium (3.47 vs 3.36 ATM), American calls on non-dividend stock do not.
- Delta hedging neutralises first-order risk; residual P&L stems from gamma and discrete rebalancing.
- Asian options are cheaper than vanilla because averaging lowers effective volatility.

**Recommendations**
- Use N ≥ 100 (≥ 200 for high σ); prefer trinomial for smoother convergence.
- Rebalance hedges more often or add gamma/vega hedges for larger P&L stability.
- Price Asian options with control-variate Monte Carlo and report standard errors.

**Corrections made in this app vs. the submitted materials** (see Documentation → Audit): the notebook's trinomial-European function
under-priced the ATM call (3.81 vs 4.61); the Asian put of 35.09 and the 3-step hedging table were not valid/real results; the Vega is
now also shown per 1 vol-point.""")
with t3:
    ui.pdf_viewer(pdf)
    st.caption("If the viewer is blocked by your browser, use the download button above.")
ui.disclaimer()
