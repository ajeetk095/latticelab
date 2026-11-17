import numpy as np, pandas as pd, plotly.graph_objects as go, plotly.express as px, streamlit as st
from utils import ui, pricing as P, explain as E

ui.hero("🔍 Explainability Dashboard",
        "Exact Shapley attribution (a SHAP-style explanation for a deterministic pricing model), sensitivities, correlation and what-if tests.")
S0, K, r, sg, T, N = ui.param_sidebar("exp", show_N=False)
N = 60  # speed for repeated evaluation
c = st.columns(2)
kind = c[0].radio("Option", ["call", "put"], horizontal=True)
am = c[1].toggle("American exercise", False)
base = dict(S0=S0, K=K, r=r, sigma=sg, T=T)
t1, t2, t3, t4, t5 = st.tabs(["Attribution (SHAP)", "Feature importance", "Sensitivity", "Correlation", "What-if"])

with t1:
    st.markdown("**Reference scenario** (what the price is compared to):")
    rc = st.columns(5)
    ref = dict(S0=rc[0].number_input("S₀ ref", 1.0, 10000.0, 100.0), K=rc[1].number_input("K ref", 1.0, 10000.0, 100.0),
               r=rc[2].number_input("r ref", 0.0, 0.2, 0.05, 0.005), sigma=rc[3].number_input("σ ref", 0.01, 1.5, 0.20, 0.01),
               T=rc[4].number_input("T ref", 0.05, 5.0, 0.25, 0.05))
    phi, v0, v1 = E.attribution(base, ref, kind, am, N)
    names = [E.LABELS[k] for k in E.INPUTS]; vals = [phi[k] for k in E.INPUTS]
    fig = go.Figure(go.Waterfall(x=["Reference price"] + names + ["Your price"], y=[v0] + vals + [0],
                                 measure=["absolute"] + ["relative"] * 5 + ["total"],
                                 increasing=dict(marker_color=ui.ACCENT2), decreasing=dict(marker_color=ui.WARN),
                                 totals=dict(marker_color=ui.ACCENT)))
    fig.update_layout(title=f"Price {v0:.3f} → {v1:.3f}", height=420, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    top = max(phi, key=lambda k: abs(phi[k]))
    st.success(f"Largest driver: **{E.LABELS[top]}** ({phi[top]:+.4f}). Contributions sum exactly to the price change ({v1 - v0:+.4f}).")

with t2:
    ref_default = dict(S0=100, K=100, r=.05, sigma=.2, T=.25)
    rows = []
    rng = np.random.default_rng(0)
    for _ in range(25):
        b = dict(S0=rng.uniform(80, 120), K=100, r=rng.uniform(0.0, .08), sigma=rng.uniform(.1, .5), T=rng.uniform(.1, 1.0))
        ph, _, _ = E.attribution(b, ref_default, kind, am, 30)
        rows.append({k: abs(v) for k, v in ph.items()})
    imp = pd.DataFrame(rows).mean().rename(index=E.LABELS).sort_values()
    st.plotly_chart(px.bar(imp, orientation="h", labels={"value": "mean |Shapley|", "index": ""},
                           color_discrete_sequence=[ui.ACCENT]).update_layout(showlegend=False, title="Global importance (random scenarios, K fixed)"),
                    use_container_width=True)
    st.caption("Mean absolute Shapley value over 25 random scenarios around S₀=K=100. Strike is held fixed so it shows 0.")

with t3:
    var = st.selectbox("Vary", E.INPUTS, format_func=lambda k: E.LABELS[k])
    lo, hi = {"S0": (.6 * S0, 1.4 * S0), "K": (.6 * K, 1.4 * K), "r": (0, .15), "sigma": (.05, 1.0), "T": (.05, 2.0)}[var]
    grid = np.linspace(lo, hi, 40)
    y = E.sensitivity(base, var, grid, kind, am, N)
    st.plotly_chart(px.line(x=grid, y=y, labels={"x": E.LABELS[var], "y": "Price"}, color_discrete_sequence=[ui.ACCENT]), use_container_width=True)
    heat_x = np.linspace(.6 * S0, 1.4 * S0, 15); heat_y = np.linspace(.1, .8, 15)
    Z = [[P.binomial(x, K, r, s, T, 40, kind, am) for x in heat_x] for s in heat_y]
    st.plotly_chart(go.Figure(go.Heatmap(x=heat_x, y=heat_y * 100, z=Z, colorscale="Viridis")).update_layout(
        title="Price surface: spot × volatility", xaxis_title="Spot", yaxis_title="σ (%)"), use_container_width=True)

with t4:
    rng = np.random.default_rng(1)
    samp = pd.DataFrame({"S0": rng.uniform(70, 130, 300), "r": rng.uniform(0, .08, 300), "sigma": rng.uniform(.1, .6, 300), "T": rng.uniform(.1, 1.5, 300)})
    samp["price"] = [P.binomial(a.S0, 100, a.r, a.sigma, a.T, 30, kind, am) for a in samp.itertuples()]
    cm = samp.corr()
    st.plotly_chart(px.imshow(cm, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                              title="Correlation of inputs and option price (300 random scenarios, K=100)"), use_container_width=True)

with t5:
    st.markdown("Change inputs and compare to the sidebar scenario.")
    w = st.columns(5)
    wi = dict(S0=w[0].number_input("S₀", 1.0, 10000.0, S0 * 1.1, key="w1"), K=K,
              r=w[2].number_input("r", 0.0, 0.2, r, 0.005, key="w3"),
              sigma=w[3].number_input("σ", 0.01, 1.5, min(sg * 1.25, 1.5), 0.01, key="w4"),
              T=w[4].number_input("T", 0.05, 5.0, T, 0.05, key="w5"))
    w[1].number_input("K (fixed)", value=K, disabled=True)
    a, b = E.price_fn(kind, am, N)(**base), E.price_fn(kind, am, N)(**wi)
    k = st.columns(3); ui.kpi(k[0], "Base price", f"{a:.4f}"); ui.kpi(k[1], "What-if price", f"{b:.4f}"); ui.kpi(k[2], "Change", f"{b - a:+.4f}", f"{(b / a - 1) * 100:+.1f}%" if a else "")
ui.disclaimer()
