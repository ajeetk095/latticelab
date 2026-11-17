"""LatticeLab – entry point / router. Run:  streamlit run app.py"""
import streamlit as st
from utils import ui

st.set_page_config(page_title="LatticeLab – Option Pricing AI Lab", page_icon="🌳", layout="wide",
                   initial_sidebar_state="expanded")
ui.setup()

pages = {
    "Explore": [
        st.Page("pages/1_Home.py", title="Home", icon="🏠", default=True),
        st.Page("pages/2_Live_Simulation.py", title="Live Simulation", icon="🧪"),
        st.Page("pages/3_Explainability.py", title="Explainability", icon="🔍"),
        st.Page("pages/4_Real_Time_Data.py", title="Real-Time Data", icon="📡"),
        st.Page("pages/11_Analytics.py", title="Advanced Analytics", icon="📊"),
        st.Page("pages/12_Ask_the_Model.py", title="Ask the Model", icon="💬"),
    ],
    "Learn & Read": [
        st.Page("pages/5_Learn.py", title="How the Model Works", icon="🎓"),
        st.Page("pages/6_Research_Report.py", title="Research Report", icon="📄"),
        st.Page("pages/7_Presentation.py", title="Presentation", icon="🎞️"),
    ],
    "Project": [
        st.Page("pages/8_About_Developer.py", title="About Developer", icon="👤"),
        st.Page("pages/9_Contact.py", title="Contact", icon="✉️"),
        st.Page("pages/10_Documentation.py", title="Documentation", icon="📚"),
    ],
}
nav = st.navigation(pages)
with st.sidebar:
    st.caption("🌳 **LatticeLab** · v1.0.0 · educational use only")
nav.run()
