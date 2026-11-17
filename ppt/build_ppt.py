"""Generate the 15-slide deck.  python ppt/build_ppt.py  (+ PDF via LibreOffice if available)"""
import io, subprocess, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from utils import pricing as P

BG, ACC, ACC2, TXT, MUTE = RGBColor(0x14, 0x12, 0x2B), RGBColor(0x6C, 0x5C, 0xE7), RGBColor(0x00, 0xCE, 0xC9), RGBColor(255, 255, 255), RGBColor(0xB8, 0xB5, 0xD6)
A = dict(S0=100, K=100, r=.05, sigma=.2, T=.25)
prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
blank = prs.slide_layouts[6]

def fig_png(fig):
    b = io.BytesIO(); fig.savefig(b, format="png", dpi=160, bbox_inches="tight", facecolor="#14122B"); plt.close(fig); b.seek(0); return b

def style_ax(ax):
    ax.set_facecolor("#14122B")
    for s in ax.spines.values(): s.set_color("#6b6890")
    ax.tick_params(colors="#B8B5D6"); ax.xaxis.label.set_color("#B8B5D6"); ax.yaxis.label.set_color("#B8B5D6"); ax.title.set_color("white")
    ax.grid(alpha=.15)

def slide(title, n, bullets=None, img=None, notes=None, table=None):
    s = prs.slides.add_slide(blank)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = BG
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(.25), prs.slide_height); bar.fill.solid(); bar.fill.fore_color.rgb = ACC; bar.line.fill.background()
    t = s.shapes.add_textbox(Inches(.7), Inches(.4), Inches(12), Inches(1)).text_frame; t.text = title
    t.paragraphs[0].font.size = Pt(34); t.paragraphs[0].font.bold = True; t.paragraphs[0].font.color.rgb = TXT
    f = s.shapes.add_textbox(Inches(.7), Inches(7.0), Inches(12), Inches(.4)).text_frame
    f.text = f"LatticeLab · Group 9450 · MScFE 620 GWP1 · {n}/15 · Educational use only"; f.paragraphs[0].font.size = Pt(10); f.paragraphs[0].font.color.rgb = MUTE
    w = Inches(6.3) if img else Inches(12)
    if bullets:
        tb = s.shapes.add_textbox(Inches(.7), Inches(1.5), w, Inches(5.3)).text_frame; tb.word_wrap = True
        for i, b in enumerate(bullets):
            p = tb.paragraphs[0] if i == 0 else tb.add_paragraph(); p.text = "▸ " + b; p.font.size = Pt(20); p.font.color.rgb = TXT; p.space_after = Pt(12)
    if img: s.shapes.add_picture(img, Inches(7.2), Inches(1.5), width=Inches(5.7))
    if table:
        rows, cols = len(table), len(table[0])
        tbl = s.shapes.add_table(rows, cols, Inches(.7), Inches(1.6), Inches(11.9), Inches(.5) * rows).table
        for i, r in enumerate(table):
            for j, v in enumerate(r):
                c = tbl.cell(i, j); c.text = str(v); c.text_frame.paragraphs[0].font.size = Pt(16)
                c.fill.solid(); c.fill.fore_color.rgb = ACC if i == 0 else RGBColor(0x24, 0x21, 0x4A); c.text_frame.paragraphs[0].font.color.rgb = TXT
    if notes: s.notes_slide.notes_text_frame.text = notes
    return s

# charts
steps = [5, 10, 25, 50, 100, 200, 400]; bs = P.black_scholes(**A)
fig, ax = plt.subplots(figsize=(6, 4)); ax.plot(steps, [P.binomial(**A, N=n) for n in steps], "o-", color="#6C5CE7", label="Binomial")
ax.plot(steps, [P.trinomial(**A, N=n) for n in steps], "s-", color="#00CEC9", label="Trinomial"); ax.axhline(bs, color="#FD79A8", ls="--", label="Black–Scholes")
ax.set_xscale("log"); ax.set_xlabel("Steps N"); ax.set_ylabel("Call price"); ax.set_title("Convergence"); ax.legend(facecolor="#14122B", labelcolor="white"); style_ax(ax); conv = fig_png(fig)
spots = np.linspace(60, 140, 60); fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(spots, [P.binomial(s, 100, .05, .2, .25, 100, "put") for s in spots], color="#6C5CE7", label="European put")
ax.plot(spots, [P.binomial(s, 100, .05, .2, .25, 100, "put", True) for s in spots], color="#FD79A8", label="American put"); ax.plot(spots, np.maximum(100 - spots, 0), "--", color="#B8B5D6", label="Payoff")
ax.set_xlabel("Spot"); ax.set_title("American vs European put"); ax.legend(facecolor="#14122B", labelcolor="white"); style_ax(ax); amer = fig_png(fig)
fig, ax = plt.subplots(figsize=(6, 4)); ks = np.arange(80, 121, 5)
ax.plot(ks, [P.binomial(100, k, .05, .2, .25, 100, "call", True) for k in ks], color="#00CEC9", label="Call"); ax.plot(ks, [P.binomial(100, k, .05, .2, .25, 100, "put", True) for k in ks], color="#FD79A8", label="Put")
ax.set_xlabel("Strike"); ax.set_title("American price vs strike (EDA)"); ax.legend(facecolor="#14122B", labelcolor="white"); style_ax(ax); eda = fig_png(fig)
rows, pnl, path = P.delta_hedge(100, 100, .05, .2, .25, 50, "call", seed=7, N=60)
fig, ax = plt.subplots(figsize=(6, 4)); ax.plot([r["t"] for r in rows], [r["portfolio"] for r in rows], color="#6C5CE7"); ax.set_title("Hedged portfolio P&L (50 rebalances)"); ax.set_xlabel("t (years)"); style_ax(ax); hedge = fig_png(fig)
call, put = P.binomial(**A, N=100), P.binomial(**A, N=100, kind="put"); g = P.greeks(**A, N=100)
asian = P.asian_mc(**A, kind="put")

# title
s = prs.slides.add_slide(blank); s.background.fill.solid(); s.background.fill.fore_color.rgb = BG
tf = s.shapes.add_textbox(Inches(.9), Inches(2.2), Inches(11.5), Inches(3)).text_frame; tf.word_wrap = True
tf.text = "🌳 LatticeLab"; tf.paragraphs[0].font.size = Pt(60); tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.color.rgb = TXT
for t, sz, c in [("Option Pricing with Binomial & Trinomial Trees, Put–Call Parity, Delta Hedging and Asian Options", 26, ACC2), ("MScFE 620 Derivative Pricing · Group Work Project #1 · Group 9450 · Presented by Ajeet Kumar", 16, MUTE)]:
    p = tf.add_paragraph(); p.text = t; p.font.size = Pt(sz); p.font.color.rgb = c
slide("Problem Statement", 2, ["Closed-form Black–Scholes cannot handle early exercise or path-dependent payoffs", "How do we price American and Asian options consistently?", "How good are lattice prices versus the analytic benchmark?", "How do traders hedge the resulting risk?"])
slide("Research Objectives", 3, ["Implement CRR binomial and Boyle trinomial trees (European & American)", "Verify put–call parity and American no-arbitrage bounds", "Estimate Delta and Vega by finite differences", "Simulate dynamic delta hedging", "Price an Asian option", "Deliver everything as an interactive, explainable web app"])
slide("Dataset Overview", 4, ["No historical dataset – this is a pricing model, not supervised ML", "Inputs: S₀, K, r, σ, T, N (scenario parameters)", "Base case: S₀=K=100, r=5%, σ=20%, T=0.25y, N=100", "Hedging case: S₀=180, K=182, r=2%, σ=25%, T=0.5y", "App adds optional live data: Yahoo Finance (free) with demo fallback"])
slide("Methodology", 5, ["Discretise time into N steps", "Build recombining price lattice (u, d, p)", "Backward induction with risk-neutral discounting", "American: max(continuation, intrinsic) at every node", "Validate vs Black–Scholes and parity identities"])
slide("Data Preprocessing", 6, ["Validate inputs: positive S, K, σ, T; r in sensible range", "Risk-neutral probability must lie in (0,1) – checked via N", "Annualise: r, σ as decimals; T in years", "CSV batch upload: schema check, row cap, error capture", "Live data: tz-naive dates, realised vol = std(log returns)·√252"])
slide("Exploratory Analysis", 7, ["American call price falls with strike; put rises", "Both increase with volatility and maturity", "Early-exercise premium appears only for puts (no dividends)"], eda)
slide("Feature Engineering", 8, ["Derived quantities: intrinsic value, time value, moneyness S/K", "Greeks: Delta, Gamma (central diff.), Vega (vol bump)", "Exact Shapley attribution over 5 inputs", "Price surfaces: spot × volatility"])
slide("Model Development", 9, ["Vectorised NumPy lattice – O(N²) with no Python inner loop", "Trinomial: u=e^{σ√(2Δt)}, Boyle probabilities", "Asian: seeded Monte-Carlo + geometric control variate", "Delta hedge: self-financing, cash earns e^{rΔt}", "10-test pytest suite incl. original notebook values"])
slide("Results", 10, [f"European call {call:.4f} | put {put:.4f}", f"Delta call {g['delta']:.4f} | Vega {g['vega']:.2f} (per 1.00σ)", "American calls: 11.67, 7.72, 4.61, 2.49, 1.19", "American puts: 0.56, 1.58, 3.47, 6.43, 10.33", f"Asian put ≈ {asian['price']:.3f} ± {1.96 * asian['stderr']:.3f}"], amer)
slide("Performance Metrics (pricing quality)", 11, [f"Black–Scholes call = {bs:.4f}", f"Binomial N=100 error = {call - bs:+.4f}", f"Trinomial N=100 error = {P.trinomial(**A, N=100) - bs:+.4f}", "Parity residual ≈ 1e-12", "No accuracy/F1/RMSE: there is no labelled data"], conv)
slide("Live Demo Architecture", 12, ["Streamlit router → 11 pages", "utils/pricing.py – core engine", "utils/explain.py – Shapley, sensitivity, assistant", "api/market.py – cached Yahoo Finance + demo mode", "Deploy: Streamlit Cloud · HF Spaces · Render · Railway · Docker"], hedge)
slide("Insights & Recommendations", 13, ["Use N ≥ 100 (more for high σ); trinomial converges more smoothly", "American puts: check early-exercise premium, esp. high r", "Hedge more often to cut gamma-driven P&L", "Report Monte-Carlo standard errors for Asian options", "Source-project defects found and corrected (see Documentation)"])
slide("Future Scope", 14, ["Dividends & discrete cash flows", "Stochastic volatility (Heston) and local vol", "Calibration to live option chains / implied-vol surface", "Exotics: barrier, lookback; GPU Monte Carlo", "Auth, saved scenarios and API endpoint"])
s = prs.slides.add_slide(blank); s.background.fill.solid(); s.background.fill.fore_color.rgb = BG
tf = s.shapes.add_textbox(Inches(.9), Inches(2.4), Inches(11.5), Inches(3)).text_frame; tf.text = "Thank You"; tf.paragraphs[0].font.size = Pt(60); tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.color.rgb = TXT
for t, c in [("Ajeet Kumar · ajeetk095@gmail.com", ACC2), ("Educational, research and demonstration purposes only – not financial advice.", MUTE)]:
    p = tf.add_paragraph(); p.text = t; p.font.size = Pt(20); p.font.color.rgb = c
assert len(prs.slides) == 15, len(prs.slides)
out = ROOT / "ppt" / "LatticeLab_Presentation.pptx"; prs.save(out); print("saved", out)
try:
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out.parent), str(out)], check=True, capture_output=True, timeout=180); print("pdf ok")
except Exception as e:
    print("PDF skipped:", e)
