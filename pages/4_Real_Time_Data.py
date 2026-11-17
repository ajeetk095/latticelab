import plotly.graph_objects as go, streamlit as st
from utils import ui, pricing as P
from api import market

ui.hero("📡 Real-Time Data", "Live prices and volatility from free Yahoo Finance data (no API key). Falls back to demo mode automatically.")
c = st.columns([2, 1, 1, 1])
ticker = c[0].text_input("Ticker", "AAPL").strip().upper()
period = c[1].selectbox("History", ["1mo", "3mo", "6mo", "1y"], index=2)
auto = c[2].toggle("Auto-refresh (60 s)", False)
if c[3].button("🔄 Refresh now"): market.get_history.clear(); market.get_risk_free.clear()

def body():
    df, err = market.get_history(ticker, period)
    demo = df is None
    if demo:
        st.warning(f"Live data unavailable ({err}). **Demo mode**: showing a deterministic synthetic series.")
        df = market.demo_history()
    spot = float(df["Close"].iloc[-1]); vol = market.realised_vol(df)
    rf, _ = market.get_risk_free(); rf = rf if rf is not None else 0.045
    k = st.columns(4)
    ui.kpi(k[0], "Last close", f"{spot:,.2f}", "DEMO" if demo else ticker)
    ui.kpi(k[1], "30-day realised vol", f"{vol:.1%}")
    ui.kpi(k[2], "Risk-free (13w T-bill)", f"{rf:.2%}", "fallback 4.5%" if rf == 0.045 else "^IRX")
    ui.kpi(k[3], "Data points", f"{len(df)}")
    fig = go.Figure(go.Scatter(x=df["Date"], y=df["Close"], line=dict(color=ui.ACCENT, width=2)))
    fig.update_layout(height=340, margin=dict(t=20), yaxis_title="Close")
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Price an option on this underlying")
    cc = st.columns(3)
    K = cc[0].number_input("Strike", 1.0, 100000.0, float(round(spot)), 1.0)
    T = cc[1].slider("Maturity (years)", .05, 2.0, .25, .05)
    am = cc[2].toggle("American", False)
    call = P.binomial(spot, K, rf, vol, T, 150, "call", am); put = P.binomial(spot, K, rf, vol, T, 150, "put", am)
    k2 = st.columns(2); ui.kpi(k2[0], "Call (model)", f"{call:.4f}", f"σ={vol:.1%}, r={rf:.2%}"); ui.kpi(k2[1], "Put (model)", f"{put:.4f}")
    st.caption("Model prices use realised vol as a stand-in for implied vol – they will differ from traded quotes.")

if auto:
    st.fragment(body, run_every=60)()
else:
    body()
with st.expander("Why not true tick-level real-time?"):
    st.write("Free endpoints are delayed/rate-limited; data are cached 5 min. The pricing model itself is deterministic, so "
             "'real-time' here means feeding current spot, volatility and rate into the lattice.")
ui.disclaimer()
