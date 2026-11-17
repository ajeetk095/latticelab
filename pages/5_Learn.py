import numpy as np, plotly.graph_objects as go, streamlit as st
from utils import ui, pricing as P

ui.hero("🎓 Learn: How This Model Works", "A beginner-friendly tour from inputs to price – no finance degree needed.")
st.subheader("1 · The big idea")
st.markdown("""An **option** gives you the *right* (not the obligation) to buy (**call**) or sell (**put**) a stock at a fixed **strike** price on or before a future date.
What is that right worth *today*? We can't know where the stock will go – but we can build a **tree of possible prices** and work backwards from the end.""")
st.subheader("2 · Input → Processing → Output")
ui.flow([("Input", "Spot S₀, strike K, rate r, volatility σ, maturity T, steps N"),
         ("Processing", "Build price tree · compute risk-neutral probability · backward induction"),
         ("Prediction", "Option price"), ("Explanation", "Greeks · Shapley attribution · checks")])
st.subheader("3 · Step-by-step workflow")
for i, t in enumerate([
    "**Split time** into N small steps of length Δt = T/N.",
    "**Build the tree**: each step the stock goes up by factor u = e^(σ√Δt) or down by d = 1/u (trinomial adds 'stays the same').",
    "**Compute payoffs** at expiry: max(S−K, 0) for calls, max(K−S, 0) for puts.",
    "**Risk-neutral probability** p = (e^(rΔt) − d)/(u − d) – a pricing device, not a forecast.",
    "**Roll back**: value = e^(−rΔt)·[p·V_up + (1−p)·V_down]. For American options also take max(value, immediate exercise).",
    "**Read the price** at the root, and estimate Greeks by bumping inputs slightly.",
    "**Sanity-check**: compare to Black–Scholes and put–call parity."], 1):
    st.markdown(f"{i}. {t}")
st.subheader("4 · Try a mini tree")
c = st.columns(3)
S0 = c[0].number_input("S₀", 1.0, 500.0, 100.0); sg = c[1].slider("σ", .05, .8, .3); steps = c[2].slider("Steps (display)", 2, 6, 4)
u = np.exp(sg * np.sqrt(.25 / steps))
xs, ys, txt = [], [], []
for i in range(steps + 1):
    for j in range(i + 1):
        xs.append(i); ys.append(i - 2 * j); txt.append(f"{S0 * u ** (i - j) / u ** j:.1f}")
fig = go.Figure()
for i in range(steps):
    for j in range(i + 1):
        fig.add_scatter(x=[i, i + 1], y=[i - 2 * j, i + 1 - 2 * j], mode="lines", line=dict(color="rgba(128,128,160,.5)"), showlegend=False)
        fig.add_scatter(x=[i, i + 1], y=[i - 2 * j, i - 1 - 2 * j], mode="lines", line=dict(color="rgba(128,128,160,.5)"), showlegend=False)
fig.add_scatter(x=xs, y=ys, mode="markers+text", text=txt, textposition="top center", marker=dict(size=26, color=ui.ACCENT, opacity=.25), showlegend=False)
fig.update_layout(height=380, xaxis_title="Step", yaxis_visible=False, margin=dict(t=10)); st.plotly_chart(fig, use_container_width=True)
st.subheader("5 · How to read the results")
st.markdown("""| Output | Meaning |
|---|---|
| **Price** | Fair value today under the model |
| **Delta** | Price change per $1 move in the stock; also the hedge ratio |
| **Gamma** | How fast delta itself changes |
| **Vega** | Price change per 1 vol-point |
| **Parity residual** | ≈0 means the pricer is internally consistent |
| **Error vs BS** | How close the tree is to the closed-form answer |""")
st.subheader("6 · FAQ")
for q, a in [("Is this machine learning?", "No. It is a numerical pricing model. The 'AI' layer here is explainability (Shapley attribution), an assistant and interactive analytics."),
             ("Why is there no accuracy score?", "There is no training data or labels. Quality is measured against Black–Scholes and no-arbitrage identities."),
             ("Why does a bigger N help?", "More steps approximate continuous price movement better; error shrinks roughly like 1/N."),
             ("Can I trade on these numbers?", "No – this is an educational tool.")]:
    with st.expander(q): st.write(a)
ui.disclaimer()
