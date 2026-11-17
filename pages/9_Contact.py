import re, smtplib, urllib.parse
from email.message import EmailMessage
import streamlit as st
from utils import ui

ui.hero("✉️ Contact the Developer", "Send a message – delivered by e-mail if SMTP is configured, otherwise opens your mail app.")
D = ui.DEV
with st.form("contact"):
    name = st.text_input("Name *"); email = st.text_input("Email *"); msg = st.text_area("Message *", height=160)
    ok = st.form_submit_button("Send", type="primary")
if ok:
    errs = []
    if len(name.strip()) < 2: errs.append("Please enter your name.")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()): errs.append("Please enter a valid email address.")
    if len(msg.strip()) < 10: errs.append("Message must be at least 10 characters.")
    if errs:
        for e in errs: st.error(e)
    else:
        try:
            s = st.secrets["smtp"]
            m = EmailMessage(); m["Subject"] = f"LatticeLab message from {name}"; m["From"] = s["user"]; m["To"] = D["email"]; m["Reply-To"] = email
            m.set_content(msg)
            with smtplib.SMTP_SSL(s["host"], int(s.get("port", 465))) as srv: srv.login(s["user"], s["password"]); srv.send_message(m)
            st.success("Message sent – thank you!")
        except Exception:
            url = f"mailto:{D['email']}?subject={urllib.parse.quote('LatticeLab message from ' + name)}&body={urllib.parse.quote(msg + chr(10) + chr(10) + '— ' + name + ' (' + email + ')')}"
            st.info("Direct sending isn't configured on this deployment, so use the button below to send from your mail app.")
            st.link_button("📨 Open in mail app", url)
st.markdown("#### Quick connect")
c = st.columns(3)
c[0].link_button("✉️ Email", f"mailto:{D['email']}", use_container_width=True)
c[1].link_button("💼 LinkedIn", D["linkedin"], use_container_width=True)
c[2].link_button("🐙 GitHub", D["github"], use_container_width=True)
ui.disclaimer()
