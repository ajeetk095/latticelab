"""Explainability + the rule-based 'Ask the Model' assistant (no external LLM / API key needed)."""
from __future__ import annotations
import math
import numpy as np
from . import pricing as P

INPUTS = ["S0", "K", "r", "sigma", "T"]
LABELS = {"S0": "Spot S₀", "K": "Strike K", "r": "Rate r", "sigma": "Volatility σ", "T": "Maturity T"}


def price_fn(kind, american=False, N=100):
    def f(S0, K, r, sigma, T):
        return P.binomial(float(S0), float(K), float(r), float(sigma), float(T), N, kind, american)
    return f


def attribution(base: dict, ref: dict, kind="call", american=False, N=100):
    phi, v0, v1 = P.shapley_attribution(price_fn(kind, american, N), base, ref)
    return {k: float(x) for k, x in phi.items()}, float(v0), float(v1)


def sensitivity(base: dict, name, grid, kind="call", american=False, N=100):
    f = price_fn(kind, american, N)
    out = []
    for g in grid:
        args = dict(base); args[name] = g
        out.append(f(**args))
    return np.array(out)


def moneyness_label(S0, K):
    m = S0 / K
    if m > 1.02: return "in-the-money (call) / out-of-the-money (put)"
    if m < 0.98: return "out-of-the-money (call) / in-the-money (put)"
    return "at-the-money"


def interpret(S0, K, r, sigma, T, N, kind, american):
    price = P.binomial(S0, K, r, sigma, T, N, kind, american)
    bs = P.black_scholes(S0, K, r, sigma, T, kind)
    g = P.greeks(S0, K, r, sigma, T, N, kind, american)
    intrinsic = max(S0 - K, 0) if kind == "call" else max(K - S0, 0)
    tv = price - intrinsic
    # "confidence": how close the lattice is to the analytical benchmark (a numerical-reliability score)
    rel_err = abs(price - bs) / max(bs, 1e-9) if not american else None
    conf = None if rel_err is None else max(0.0, min(1.0, 1 - rel_err * 20))
    lines = [f"The {'American' if american else 'European'} {kind} is {moneyness_label(S0, K)} "
             f"(S₀/K = {S0 / K:.2f}) and is worth **{price:.4f}**.",
             f"Intrinsic value is {intrinsic:.4f}; the remaining {tv:.4f} is time value that you pay for the chance "
             f"the stock moves favourably before {T:.2f}y."]
    d = g["delta"]
    lines.append(f"Delta {d:+.3f}: a $1 move in the stock changes the option by roughly ${abs(d):.2f}; "
                 f"a hedger would hold {-d:+.3f} shares per option sold.")
    lines.append(f"Vega {g['vega_1pct']:.3f} per vol-point: if volatility rises by 1 percentage point, the price rises by ~{g['vega_1pct']:.3f}.")
    rec = []
    if tv / max(price, 1e-9) > 0.8: rec.append("Most of the price is time value – it decays quickly as expiry approaches.")
    if abs(d) > 0.8: rec.append("Deep in/out of the money: behaves almost like the stock itself (or worthless).")
    if sigma > 0.5: rec.append("Very high volatility – lattice needs larger N for accuracy.")
    if N < 50: rec.append("N is small; increase N ≥ 100 for stable prices.")
    if american and kind == "put" and r > 0:
        eu = P.binomial(S0, K, r, sigma, T, N, "put", False)
        rec.append(f"Early-exercise premium: {price - eu:.4f} (American − European put).")
    if not rec: rec.append("Inputs are in a numerically comfortable regime.")
    return dict(price=price, bs=bs, greeks=g, intrinsic=intrinsic, time_value=tv, confidence=conf,
                summary=lines, recommendations=rec)


KB = [
    (("delta",), "Delta is the sensitivity of the option price to the stock price (∂V/∂S). In the tree it is "
                 "estimated by finite differences. Calls have delta in (0,1); puts in (−1,0)."),
    (("vega", "volatility"), "Vega measures sensitivity to volatility. Higher σ means wider trees and a higher "
                             "option value for both calls and puts."),
    (("parity", "pcp"), "Put–call parity (European): C − P = S₀ − K·e^{−rT}. For American options only the bounds "
                        "S₀ − K ≤ C − P ≤ S₀ − K·e^{−rT} hold."),
    (("american", "early"), "American options can be exercised any time; at each node the model takes max(continuation, "
                            "intrinsic). Early exercise is valuable mainly for puts (high r) and dividend-paying calls."),
    (("trinomial",), "Trinomial trees add a middle 'unchanged' branch (Boyle). They converge faster/smoother than binomial "
                     "trees for the same number of steps."),
    (("binomial", "crr"), "CRR binomial tree: u = e^{σ√Δt}, d = 1/u, p = (e^{rΔt} − d)/(u − d). Price by backward induction "
                          "with risk-neutral discounting."),
    (("asian",), "Asian options pay off on the average price, so they are cheaper than vanilla options (less volatile "
                 "average). The app uses seeded Monte-Carlo with an exact geometric-Asian control variate."),
    (("hedge", "hedging"), "Delta hedging holds −Δ shares per option sold and rebalances periodically. Residual P&L comes "
                           "from gamma (discrete rebalancing) and realised-vs-implied volatility."),
    (("shap", "explain", "attribution"), "Because the pricer is a deterministic model rather than a trained ML model, the app "
                                         "uses exact Shapley values over the five inputs (S₀, K, r, σ, T) to attribute a price "
                                         "change versus a reference scenario."),
    (("dataset", "data", "ml", "machine"), "This project is quantitative finance, not supervised ML: there is no training dataset. "
                                           "Inputs are market parameters; 'metrics' are pricing-quality measures (error vs Black–Scholes, parity residual)."),
]


def ask(question: str, ctx: dict | None = None) -> str:
    q = question.lower()
    hits = [t for keys, t in KB if any(k in q for k in keys)]
    if ctx and any(w in q for w in ("price", "worth", "value", "current", "scenario", "recommend", "insight")):
        r = interpret(**ctx)
        hits.insert(0, "For your current inputs: " + " ".join(r["summary"]) + "\n\n**Recommendations:** " + " ".join(r["recommendations"]))
    if not hits:
        return ("I can explain delta, vega, put–call parity, American vs European, binomial/trinomial trees, Asian options, "
                "hedging, explainability, or interpret your current scenario. Try: *'What is delta?'* or *'Interpret my scenario'*.")
    return "\n\n".join(hits)
