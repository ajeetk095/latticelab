import io
import numpy as np, pandas as pd, plotly.graph_objects as go, plotly.express as px, streamlit as st
from utils import ui, pricing as P, explain as E

ui.hero("🧪 Live Simulation", "Enter inputs manually, upload a CSV of scenarios, or compare several scenarios side by side.")
tab1, tab2, tab3 = st.tabs(["Manual entry", "CSV upload (batch)", "Multi-scenario"])

with tab1:
    S0, K, r, sg, T, N = ui.param_sidebar("sim")
    c1, c2, c3 = st.columns(3)
    kind = c1.radio("Option type", ["call", "put"], horizontal=True)
    style = c2.radio("Exercise", ["European", "American"], horizontal=True)
    model = c3.radio("Lattice", ["Binomial", "Trinomial"], horizontal=True)
    am = style == "American"
    price = (P.binomial if model == "Binomial" else P.trinomial)(S0, K, r, sg, T, N, kind, am)
    res = E.interpret(S0, K, r, sg, T, N, kind, am)
    k = st.columns(4)
    ui.kpi(k[0], f"{style} {kind} price", f"{price:.4f}", model)
    ui.kpi(k[1], "Black–Scholes (Euro.)", f"{res['bs']:.4f}", "analytic benchmark")
    conf = res["confidence"]
    ui.kpi(k[2], "Numerical confidence", "n/a" if conf is None else f"{conf:.0%}", "closeness to BS")
    ui.kpi(k[3], "Time value", f"{res['time_value']:.4f}", f"intrinsic {res['intrinsic']:.4f}")
    g = res["greeks"]
    gcols = st.columns(3)
    ui.kpi(gcols[0], "Delta", f"{g['delta']:+.4f}"); ui.kpi(gcols[1], "Gamma", f"{g['gamma']:.4f}")
    ui.kpi(gcols[2], "Vega (per 1 vol-pt)", f"{g['vega_1pct']:.4f}")

    st.markdown("#### Plain-language interpretation")
    for l in res["summary"]: st.markdown("- " + l)
    st.markdown("#### Recommendations / insights")
    for l in res["recommendations"]: st.info(l)

    spots = np.linspace(0.5 * S0, 1.5 * S0, 60)
    pv = [P.binomial(s, K, r, sg, T, min(N, 100), kind, am) for s in spots]
    payoff = np.maximum(spots - K, 0) if kind == "call" else np.maximum(K - spots, 0)
    fig = go.Figure()
    fig.add_scatter(x=spots, y=pv, name="Option value", line=dict(color=ui.ACCENT, width=3))
    fig.add_scatter(x=spots, y=payoff, name="Payoff at expiry", line=dict(color=ui.WARN, dash="dash"))
    fig.add_vline(x=S0, line_dash="dot", annotation_text="S₀")
    fig.update_layout(title="Value vs spot", xaxis_title="Spot", yaxis_title="Value", height=380, margin=dict(t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("Upload a CSV with columns **S0, K, r, sigma, T** (optional: **N, kind, american**). *r* and *sigma* as decimals (0.05 = 5 %).")
    sample = pd.DataFrame({"S0": [100, 100, 180], "K": [95, 105, 182], "r": [.05, .05, .02], "sigma": [.2, .2, .25],
                           "T": [.25, .25, .5], "N": [100, 100, 100], "kind": ["call", "put", "put"], "american": [False, True, False]})
    st.download_button("⬇️ Download sample CSV", sample.to_csv(index=False), "sample_scenarios.csv", "text/csv")
    up = st.file_uploader("Scenarios CSV", type="csv")
    df = pd.read_csv(up) if up else sample
    if not up: st.caption("Showing sample data until you upload a file.")
    miss = {"S0", "K", "r", "sigma", "T"} - set(df.columns)
    if miss:
        st.error(f"Missing columns: {', '.join(sorted(miss))}")
    elif len(df) > 500:
        st.error("Max 500 rows.")
    else:
        out = []
        for _, row in df.iterrows():
            kd = str(row.get("kind", "call")).lower(); n = int(row.get("N", 100))
            am_ = str(row.get("american", False)).lower() in ("true", "1", "yes")
            try:
                pr = P.binomial(row.S0, row.K, row.r, row.sigma, row["T"], n, kd, am_)
                gg = P.greeks(row.S0, row.K, row.r, row.sigma, row["T"], n, kd, am_)
                out.append({**row.to_dict(), "price": pr, "delta": gg["delta"], "vega_1pct": gg["vega_1pct"]})
            except Exception as e:
                out.append({**row.to_dict(), "price": np.nan, "error": str(e)})
        o = pd.DataFrame(out); st.dataframe(o.style.format(precision=4), use_container_width=True)
        st.download_button("⬇️ Download results", o.to_csv(index=False), "results.csv", "text/csv")

with tab3:
    st.markdown("Compare up to 4 scenarios (changes relative to the sidebar base case).")
    base = dict(S0=S0, K=K, r=r, sigma=sg, T=T)
    n = st.slider("Scenarios", 2, 4, 3)
    rows = []
    cols = st.columns(n)
    for i, c in enumerate(cols):
        with c:
            st.markdown(f"**Scenario {i + 1}**")
            s_ = c.number_input("Spot", 1.0, 10000.0, float(S0 * (1 + 0.05 * (i - 1))), key=f"ms_s{i}")
            v_ = c.slider("σ %", 1, 120, int(sg * 100) + 5 * i, key=f"ms_v{i}") / 100
            rows.append((f"Scenario {i + 1}", s_, v_))
    recs = []
    for name, s_, v_ in rows:
        for kd in ("call", "put"):
            recs.append({"Scenario": name, "Type": kd, "Price": P.binomial(s_, K, r, v_, T, N, kd, False)})
    d = pd.DataFrame(recs)
    st.plotly_chart(px.bar(d, x="Scenario", y="Price", color="Type", barmode="group",
                           color_discrete_sequence=ui.PALETTE), use_container_width=True)
    st.dataframe(d.pivot(index="Scenario", columns="Type", values="Price").style.format(precision=4))
ui.disclaimer()
