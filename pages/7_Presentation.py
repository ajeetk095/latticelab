import streamlit as st
from utils import ui

ui.hero("🎞️ Presentation", "A 15-slide deck generated from the project (Problem → Data → Method → Results → Roadmap).")
d = ui.ROOT / "ppt"
pp, pf = d / "LatticeLab_Presentation.pptx", d / "LatticeLab_Presentation.pdf"
c = st.columns(2)
if pp.exists(): c[0].download_button("⬇️ Download PPTX", pp.read_bytes(), pp.name, "application/vnd.openxmlformats-officedocument.presentationml.presentation", use_container_width=True)
else: c[0].warning("Run `python ppt/build_ppt.py` to generate the deck.")
if pf.exists(): c[1].download_button("⬇️ Download PDF", pf.read_bytes(), pf.name, "application/pdf", use_container_width=True)
if pf.exists(): ui.pdf_viewer(pf, 560)
ui.disclaimer()
