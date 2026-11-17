import streamlit as st
from utils import ui, explain as E

ui.hero("💬 Ask the Model", "A built-in rule-based assistant: Q&A, insights, explanations and recommendations about the pricing model. No API key needed.")
S0, K, r, sg, T, N = ui.param_sidebar("ask")
kind = st.radio("Scenario option type", ["call", "put"], horizontal=True)
am = st.toggle("American", False)
ctx = dict(S0=S0, K=K, r=r, sigma=sg, T=T, N=N, kind=kind, american=am)
if "chat" not in st.session_state:
    st.session_state.chat = [("assistant", "Hi! Ask about delta, vega, parity, trees, Asian options, hedging – or say **'interpret my scenario'**.")]
c = st.columns(4)
for i, q in enumerate(["What is delta?", "Interpret my scenario", "Why is American put > European put?", "How does hedging work?"]):
    if c[i].button(q, use_container_width=True): st.session_state.chat += [("user", q), ("assistant", E.ask(q, ctx))]
for role, msg in st.session_state.chat:
    with st.chat_message(role): st.markdown(msg)
if q := st.chat_input("Ask something…"):
    st.session_state.chat += [("user", q), ("assistant", E.ask(q, ctx))]; st.rerun()
ui.disclaimer()
