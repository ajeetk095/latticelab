import streamlit as st
from utils import ui

D = ui.DEV
ui.hero(f"👤 {D['name']}", "AI · Machine Learning · Quantitative Finance")
c = st.columns(3)
c[0].link_button("✉️ Email", f"mailto:{D['email']}", use_container_width=True)
c[1].link_button("💼 LinkedIn", D["linkedin"], use_container_width=True)
c[2].link_button("🐙 GitHub", D["github"], use_container_width=True)
st.caption("LinkedIn / GitHub links are placeholders – edit `DEV` in `utils/ui.py`.")
st.subheader("About me")
st.markdown("""Hi, I'm Ajeet Kumar, a quantitative finance aspiring professional based in Bangalore, India. I hold a B.Tech in Information Technology from Dr. A.P.J. Abdul Kalam Technical University and an M.Tech in Computer Science and Engineering from Netaji Subhas University of Technology, New Delhi (CGPA: 7.92). I recently graduated from WorldQuant University with an M.Sc. in Financial Engineering, scoring 88%.

My work sits at the intersection of technology and finance. I'm skilled in Python, C++, and SQL, and I've spent the last few years applying quantitative methods — Markowitz MVO, Black-Litterman, Monte Carlo Simulation — alongside machine learning techniques like Random Forest and deep learning to real problems.

I've put this into practice through projects in portfolio optimization, Fama-French factor analysis, and covariance denoising, and through internships at Amul GCMMF and Algo8.ai, where I built AI-driven defect detection systems using computer vision. Along the way, I won 1st Place at the Algo8 ML Hackathon at IIT Kanpur and was felicitated by the President of India for academic excellence.

I'm now looking to bring this mix of finance and engineering skill to a full-time role in quantitative research or financial engineering — I'd love to hear from teams working on interesting problems in that space.""")
a = st.columns(2)
ui.card(a[0], "🎓 Education", "<b>M.Sc. Financial Engineering</b>, WorldQuant University (88%)<br>"
        "<b>M.Tech, Computer Science &amp; Engineering</b>, NSUT Delhi (CGPA 7.92)<br>"
        "<b>B.Tech, Information Technology</b>, Dr. A.P.J. Abdul Kalam Technical University")
ui.card(a[1], "🛠️ Skills", " ".join(f'<span class="pill">{s}</span>' for s in
        ["Artificial Intelligence", "Machine Learning", "Data Science", "Computer Vision", "Reinforcement Learning", "Portfolio Optimization", "Python", "C++", "SQL"]))
st.subheader("Developer journey")
for i, (t, d) in enumerate([("Idea", "Turn a coursework pricing project into a product-grade app."), ("Research", "Binomial/trinomial trees, parity, hedging, Asian options."),
        ("Data", "Parameter scenarios + free market data (Yahoo Finance)."), ("Model", "Vectorised pricers, exact Shapley explanations."),
        ("Testing", "Unit tests vs Black–Scholes and parity."), ("Deployment", "Streamlit Cloud, HF Spaces, Docker, Render, Railway."),
        ("Future vision", "Stochastic vol, exotics, calibrated live surfaces, GPU Monte Carlo.")], 1):
    st.markdown(f"**{i}. {t}** — {d}")
ui.disclaimer()
