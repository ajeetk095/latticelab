import streamlit as st
from utils import ui

ui.hero("📚 Documentation", "Install, run, understand and deploy LatticeLab.")
docs = ui.ROOT / "documentation"
tabs = st.tabs(["Install & usage", "Structure", "Model details", "Data & APIs", "Audit of source project", "Troubleshooting", "Deployment", "FAQ"])
with tabs[0]:
    st.code("git clone <repo-url> && cd latticelab\npython -m venv .venv && source .venv/bin/activate\npip install -r requirements.txt\nstreamlit run app.py", "bash")
    st.write("Run tests: `pytest -q`. Rebuild deck: `python ppt/build_ppt.py`.")
with tabs[1]:
    st.code("app.py            router + navigation\npages/            11 pages\nutils/pricing.py  trees, Greeks, hedging, Asian, Shapley\nutils/explain.py  attribution, sensitivity, assistant\nutils/ui.py       CSS, KPI cards, disclaimer\napi/market.py     Yahoo Finance + demo fallback\nppt/              deck generator + outputs\nreports/          research report PDF\ndocumentation/    brief, notebook, deployment.md\ntests/            pytest suite", "text")
with tabs[2]:
    st.markdown("""- **CRR binomial**: u=e^{σ√Δt}, d=1/u, p=(e^{rΔt}−d)/(u−d). Vectorised backward induction (O(N²), NumPy).
- **Boyle trinomial**: u=e^{σ√(2Δt)}, probabilities from Boyle (1986).
- **Greeks**: central-difference Delta/Gamma (h = 1 % S₀); Vega with +5 vol-point bump (notebook convention) and per-1-point scaling.
- **Hedging**: short option, hold Δ shares, cash accrues e^{rΔt}, re-hedge each step; terminal P&L reported.
- **Asian**: arithmetic-average MC (seeded) with geometric-Asian (Kemna–Vorst) control variate.
- **Explainability**: exact Shapley values over 5 inputs (32 coalitions).
- **Metrics**: error vs Black–Scholes, parity residual, American−European premium. No ML metrics: there is no dataset.""")
with tabs[3]:
    st.markdown("Only free, key-less sources: **Yahoo Finance** via `yfinance` (cached 5 min; `^IRX` for the risk-free proxy). On failure the app switches to a deterministic demo series. "
                "Optional secret: `[smtp]` (host, port, user, password) for the contact form.")
with tabs[4]:
    st.markdown("""Issues found in the submitted notebook/report and how this app handles them:
1. `trinomial_tree_european` returned 3.81 for the ATM call (expected ≈ 4.61) → replaced by a verified Boyle implementation (4.610 at N=100).
2. Asian put = 35.09 is outside no-arbitrage bounds → replaced by control-variate Monte Carlo (~2.02).
3. The delta-hedging table was synthetic → replaced by a real simulation.
4. Several numbers quoted in the report (Q8/Q10/Q15/Q16/Q23) disagree with the notebook outputs → app uses recomputed values.
5. Vega was reported per 1.00 vol; the app also gives per-vol-point.
**Preserved unchanged:** CRR binomial pricer and American early-exercise logic – outputs match the original exactly (4.605026 / 3.362806).""")
with tabs[5]:
    st.markdown("- *Live data unavailable* → network/rate limit; demo mode is used automatically.\n- *Slow sliders* → lower N or turn off American.\n- *PDF viewer blank* → browser blocked data-URI iframes; use Download.\n- *Port busy* → `streamlit run app.py --server.port 8502`.")
with tabs[6]:
    p = docs / "deployment.md"
    st.markdown(p.read_text() if p.exists() else "See deployment.md")
with tabs[7]:
    for q, a in [("Why 'AI-powered'?", "Explainability, an assistant and analytics sit on top of a quantitative model; there is no trained ML model."), ("Is it investment advice?", "No.")]:
        with st.expander(q): st.write(a)
ui.disclaimer()
