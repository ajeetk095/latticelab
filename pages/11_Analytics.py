import numpy as np, pandas as pd, plotly.express as px, plotly.graph_objects as go, streamlit as st
from utils import ui, pricing as P, explain as E

ui.hero("📊 Advanced Analytics", "Convergence, price trends, American vs European, feature ranking and error distribution.")
S0, K, r, sg, T, N = ui.param_sidebar("an", show_N=False)
t1, t2, t3, t4, t5 = st.tabs(["Convergence", "Strike study", "Hedging", "Asian option", "Comparison & ranking"])

with t1:
    kind = st.radio("Option", ["call", "put"], horizontal=True, key="cv")
    d = pd.DataFrame(P.convergence(S0, K, r, sg, T, kind))
    f = go.Figure()
    f.add_scatter(x=d.N, y=d.Binomial, name="Binomial", mode="lines+markers"); f.add_scatter(x=d.N, y=d.Trinomial, name="Trinomial", mode="lines+markers")
    f.add_hline(y=d.BlackScholes[0], line_dash="dash", annotation_text="Black–Scholes")
    f.update_layout(xaxis_type="log", title="Convergence to Black–Scholes", height=380); st.plotly_chart(f, use_container_width=True)
    st.plotly_chart(px.line(d, x="N", y=["Binomial error", "Trinomial error"], log_x=True, title="Signed error vs Black–Scholes"), use_container_width=True)
    st.dataframe(d.style.format(precision=5), use_container_width=True)

with t2:
    ks = np.arange(0.8 * S0, 1.21 * S0, 0.05 * S0 / 1)
    rows = [{"K": k, "Euro call": P.binomial(S0, k, r, sg, T, 100, "call"), "Amer call": P.binomial(S0, k, r, sg, T, 100, "call", True),
             "Euro put": P.binomial(S0, k, r, sg, T, 100, "put"), "Amer put": P.binomial(S0, k, r, sg, T, 100, "put", True)} for k in ks]
    d = pd.DataFrame(rows); d["Early-exercise premium (put)"] = d["Amer put"] - d["Euro put"]
    st.plotly_chart(px.line(d, x="K", y=["Euro call", "Amer call", "Euro put", "Amer put"], title="Price vs strike"), use_container_width=True)
    st.plotly_chart(px.bar(d, x="K", y="Early-exercise premium (put)", color_discrete_sequence=[ui.WARN]), use_container_width=True)
    pc = P.parity_check(S0, K, r, sg, T, 100)
    pa = P.parity_check(S0, K, r, sg, T, 100, american=True)
    st.markdown(f"**Put–call parity (European):** C−P = {pc['lhs']:.6f}, S₀−Ke^(−rT) = {pc['rhs']:.6f}, residual {pc['residual']:.1e} → {'✅ holds' if pc['holds'] else '❌ violated'}.")
    st.markdown(f"**American bounds:** {pa['lower']:.4f} ≤ C−P = {pa['lhs']:.4f} ≤ {pa['upper']:.4f} → {'✅' if pa['holds'] else '❌'}")

with t3:
    c = st.columns(4)
    kind = c[0].selectbox("Short option", ["put", "call"], key="hk"); steps = c[1].slider("Rebalances", 3, 100, 12)
    seed = c[2].number_input("Random seed", 0, 9999, 7); ncp = c[3].slider("Tree steps", 20, 200, 50)
    rows, pnl, path = P.delta_hedge(S0, K, r, sg, T, steps, kind, seed=int(seed), N=ncp)
    d = pd.DataFrame(rows)
    k = st.columns(3); ui.kpi(k[0], "Final hedged P&L", f"{pnl:+.4f}", "≈0 ideal"); ui.kpi(k[1], "Final spot", f"{path[-1]:.2f}"); ui.kpi(k[2], "Initial option premium", f"{d.option[0]:.4f}")
    st.plotly_chart(px.line(d, x="t", y=["S"], title="Simulated stock path (risk-neutral GBM)"), use_container_width=True)
    st.plotly_chart(px.line(d, x="t", y=["shares", "portfolio"], title="Hedge position and portfolio value"), use_container_width=True)
    st.dataframe(d.style.format(precision=4), use_container_width=True)
    st.caption("Positive P&L means realised volatility was below the volatility used for pricing, and vice-versa; finer rebalancing shrinks the error. "
               "This replaces the placeholder table in the original notebook with a genuine simulation.")

with t4:
    kind = st.radio("Type", ["put", "call"], horizontal=True, key="ak")
    npth = st.select_slider("Monte-Carlo paths", [5000, 20000, 50000, 100000], 20000)
    a = P.asian_mc(S0, K, r, sg, T, 50, npth, kind)
    eu = P.black_scholes(S0, K, r, sg, T, kind)
    k = st.columns(4); ui.kpi(k[0], "Asian (arith.)", f"{a['price']:.4f}", f"± {1.96 * a['stderr']:.4f} (95%)"); ui.kpi(k[1], "Geometric (exact)", f"{a['geometric']:.4f}")
    ui.kpi(k[2], "European (BS)", f"{eu:.4f}"); ui.kpi(k[3], "Asian discount", f"{(1 - a['price'] / eu):.0%}")
    st.info("Averaging reduces effective volatility, so Asian options are cheaper than their European counterparts. "
            "The original notebook value of 35.09 is not a valid Asian put price for these inputs (it exceeds the strike-discount bound); "
            "this app uses control-variate Monte Carlo instead.")

with t5:
    base = dict(S0=S0, K=K, r=r, sigma=sg, T=T)
    ref = dict(S0=100, K=100, r=.05, sigma=.2, T=.25)
    rank = []
    for kd in ("call", "put"):
        ph, _, _ = E.attribution(base, ref, kd, False, 40)
        for k_, v in ph.items(): rank.append({"Option": kd, "Feature": E.LABELS[k_], "|impact|": abs(v)})
    d = pd.DataFrame(rank)
    st.plotly_chart(px.bar(d, x="Feature", y="|impact|", color="Option", barmode="group", title="Feature ranking vs reference scenario",
                           color_discrete_sequence=ui.PALETTE), use_container_width=True)
    rng = np.random.default_rng(3)
    errs = []
    for _ in range(150):
        s, k_, v, t_ = rng.uniform(80, 120), rng.uniform(80, 120), rng.uniform(.1, .6), rng.uniform(.1, 1.5)
        errs.append(P.binomial(s, k_, r, v, t_, 100, "call") - P.black_scholes(s, k_, r, v, t_, "call"))
    st.plotly_chart(px.histogram(x=errs, nbins=30, labels={"x": "Binomial(N=100) − BS"}, title="Pricing-error distribution (150 random contracts) – the 'confidence' view",
                                 color_discrete_sequence=[ui.ACCENT2]), use_container_width=True)
    st.metric("Mean absolute error", f"{np.mean(np.abs(errs)):.5f}"); st.metric("Max absolute error", f"{np.max(np.abs(errs)):.5f}")
ui.disclaimer()
