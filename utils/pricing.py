"""Core pricing engine (CRR binomial, trinomial, American, Asian, hedging).

Preserves the research logic of the original GWP1 notebook. Vectorised with NumPy.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
import numpy as np
from scipy.stats import norm


@dataclass(frozen=True)
class Params:
    S0: float = 100.0
    K: float = 100.0
    r: float = 0.05
    sigma: float = 0.20
    T: float = 0.25
    N: int = 100


def black_scholes(S0, K, r, sigma, T, kind="call"):
    if T <= 0 or sigma <= 0:
        return max(S0 - K, 0.0) if kind == "call" else max(K - S0, 0.0)
    d1 = (math.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if kind == "call":
        return S0 * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    return K * math.exp(-r * T) * norm.cdf(-d2) - S0 * norm.cdf(-d1)


def _payoff(S, K, kind):
    return np.maximum(S - K, 0.0) if kind == "call" else np.maximum(K - S, 0.0)


def binomial(S0, K, r, sigma, T, N=100, kind="call", american=False, return_tree=False):
    """CRR binomial tree. Returns price (and tree dict if requested)."""
    dt = T / N
    u = math.exp(sigma * math.sqrt(dt))
    d = 1.0 / u
    p = (math.exp(r * dt) - d) / (u - d)
    disc = math.exp(-r * dt)
    j = np.arange(N + 1)
    S = S0 * u ** (N - j) * d ** j
    V = _payoff(S, K, kind)
    vals = [V.copy()] if return_tree else None
    for i in range(N - 1, -1, -1):
        V = disc * (p * V[:-1] + (1 - p) * V[1:])
        if american:
            Si = S0 * u ** (i - np.arange(i + 1)) * d ** np.arange(i + 1)
            V = np.maximum(V, _payoff(Si, K, kind))
        if return_tree:
            vals.append(V.copy())
    if return_tree:
        return float(V[0]), {"u": u, "d": d, "p": p, "values": vals[::-1]}
    return float(V[0])


def trinomial(S0, K, r, sigma, T, N=100, kind="call", american=False):
    """Boyle trinomial tree, u = exp(sigma*sqrt(2dt)); probabilities from Boyle (1986)."""
    dt = T / N
    u = math.exp(sigma * math.sqrt(2 * dt))
    d = 1.0 / u
    a = math.exp(r * dt / 2)
    b = math.exp(sigma * math.sqrt(dt / 2))
    pu = ((a - 1 / b) / (b - 1 / b)) ** 2
    pd = ((b - a) / (b - 1 / b)) ** 2
    pm = 1 - pu - pd
    disc = math.exp(-r * dt)
    k = np.arange(-N, N + 1)
    V = _payoff(S0 * u ** k, K, kind)
    for i in range(N - 1, -1, -1):
        V = disc * (pu * V[2:] + pm * V[1:-1] + pd * V[:-2])
        if american:
            ki = np.arange(-i, i + 1)
            V = np.maximum(V, _payoff(S0 * u ** ki, K, kind))
    return float(V[0])


def greeks(S0, K, r, sigma, T, N=100, kind="call", american=False):
    """Finite-difference Delta, Gamma and Vega (vega per 1 vol-point as in notebook: +5pt bump scaled to 1.00 vol)."""
    h = 0.01 * S0
    f = lambda s, sg=sigma: binomial(s, K, r, sg, T, N, kind, american)
    up, dn, mid = f(S0 + h), f(S0 - h), f(S0)
    delta = (up - dn) / (2 * h)
    gamma = (up - 2 * mid + dn) / h**2
    bump = 0.05
    vega_per_unit = (f(S0, sigma + bump) - mid) / bump  # per 1.00 of vol (original notebook convention)
    return {"delta": delta, "gamma": gamma, "vega": vega_per_unit, "vega_1pct": vega_per_unit / 100}


def parity_check(S0, K, r, sigma, T, N=100, american=False):
    c = binomial(S0, K, r, sigma, T, N, "call", american)
    p = binomial(S0, K, r, sigma, T, N, "put", american)
    lhs = c - p
    if not american:
        rhs = S0 - K * math.exp(-r * T)
        return {"call": c, "put": p, "lhs": lhs, "rhs": rhs, "residual": lhs - rhs, "holds": abs(lhs - rhs) < 1e-6 * max(1, S0)}
    lo, hi = S0 - K, S0 - K * math.exp(-r * T)
    return {"call": c, "put": p, "lhs": lhs, "lower": lo, "upper": hi, "holds": lo - 1e-9 <= lhs <= hi + 1e-9}


def convergence(S0, K, r, sigma, T, kind="call", steps=(5, 10, 25, 50, 100, 200, 400)):
    bs = black_scholes(S0, K, r, sigma, T, kind)
    rows = []
    for n in steps:
        b, t = binomial(S0, K, r, sigma, T, n, kind), trinomial(S0, K, r, sigma, T, n, kind)
        rows.append({"N": n, "Binomial": b, "Trinomial": t, "BlackScholes": bs,
                     "Binomial error": b - bs, "Trinomial error": t - bs})
    return rows


def asian_mc(S0, K, r, sigma, T, steps=50, n_paths=20000, kind="put", seed=42):
    """Arithmetic-average Asian option by seeded Monte Carlo with geometric-Asian control variate."""
    rng = np.random.default_rng(seed)
    dt = T / steps
    z = rng.standard_normal((n_paths, steps))
    paths = S0 * np.exp(np.cumsum((r - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * z, axis=1))
    arith = paths.mean(axis=1)
    geo = np.exp(np.log(paths).mean(axis=1))
    disc = math.exp(-r * T)
    pa, pg = disc * _payoff(arith, K, kind), disc * _payoff(geo, K, kind)
    gp = asian_geometric(S0, K, r, sigma, T, steps, kind)
    c = np.cov(pa, pg)
    beta = c[0, 1] / c[1, 1] if c[1, 1] > 0 else 0
    adj = pa - beta * (pg - gp)
    return {"price": float(adj.mean()), "stderr": float(adj.std(ddof=1) / math.sqrt(n_paths)),
            "naive": float(pa.mean()), "geometric": gp}


def asian_geometric(S0, K, r, sigma, T, n=50, kind="put"):
    """Closed-form discrete geometric Asian (Kemna-Vorst)."""
    dt = T / n
    t = dt * np.arange(1, n + 1)
    mu = math.log(S0) + (r - 0.5 * sigma**2) * t.mean()
    var = sigma**2 * dt * sum((n - i + 1) ** 2 for i in range(1, n + 1)) / n**2 * 1.0
    # variance of mean of log prices
    idx = np.arange(1, n + 1)
    var = sigma**2 * dt * np.sum(((n - idx + 1) / n) ** 2)
    sd = math.sqrt(var)
    F = math.exp(mu + 0.5 * var)
    d1 = (mu - math.log(K) + var) / sd
    d2 = d1 - sd
    disc = math.exp(-r * T)
    if kind == "call":
        return disc * (F * norm.cdf(d1) - K * norm.cdf(d2))
    return disc * (K * norm.cdf(-d2) - F * norm.cdf(-d1))


def simulate_paths(S0, r, sigma, T, steps, n_paths=1, seed=7):
    rng = np.random.default_rng(seed)
    dt = T / steps
    z = rng.standard_normal((n_paths, steps))
    inc = (r - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * z
    return S0 * np.exp(np.concatenate([np.zeros((n_paths, 1)), np.cumsum(inc, axis=1)], axis=1))


def delta_hedge(S0, K, r, sigma, T, steps=3, kind="put", path=None, seed=7, N=100, american=False):
    """Dynamic delta-hedging of a short option; returns table and final P&L.

    The writer sells the option, holds delta shares, cash earns e^{r dt}.
    Path may be supplied (list of steps+1 prices) else simulated under risk-neutral GBM.
    """
    if path is None:
        path = simulate_paths(S0, r, sigma, T, steps, 1, seed)[0]
    path = np.asarray(path, float)
    dt = T / steps
    price0 = binomial(path[0], K, r, sigma, T, N, kind, american)
    delta0 = greeks(path[0], K, r, sigma, T, N, kind, american)["delta"]
    cash = price0 - delta0 * path[0]
    rows = [{"t": 0.0, "S": path[0], "delta": delta0, "shares": delta0, "cash": cash,
             "option": price0, "portfolio": delta0 * path[0] + cash - price0}]
    shares = delta0
    for i in range(1, steps + 1):
        cash *= math.exp(r * dt)
        tau = T - i * dt
        S = path[i]
        if i < steps:
            opt = binomial(S, K, r, sigma, tau, N, kind, american)
            d = greeks(S, K, r, sigma, tau, N, kind, american)["delta"]
            cash -= (d - shares) * S
            shares = d
        else:
            opt = float(_payoff(np.array(S), K, kind))
            d = shares
        rows.append({"t": i * dt, "S": S, "delta": d, "shares": shares, "cash": cash,
                     "option": opt, "portfolio": shares * S + cash - opt})
    return rows, rows[-1]["portfolio"], path


def shapley_attribution(fn, base: dict, ref: dict):
    """Exact Shapley values of fn(**inputs) moving from ref -> base across all inputs."""
    from itertools import combinations
    from math import factorial
    keys = list(base)
    n = len(keys)
    cache = {}

    def v(S):
        key = frozenset(S)
        if key not in cache:
            cache[key] = fn(**{k: (base[k] if k in key else ref[k]) for k in keys})
        return cache[key]

    phi = {}
    for k in keys:
        others = [x for x in keys if x != k]
        tot = 0.0
        for s in range(n):
            w = factorial(s) * factorial(n - s - 1) / factorial(n)
            for sub in combinations(others, s):
                tot += w * (v(set(sub) | {k}) - v(set(sub)))
        phi[k] = tot
    return phi, v(set()), v(set(keys))
