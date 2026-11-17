import math, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import pytest
from utils import pricing as P, explain as E

A = dict(S0=100, K=100, r=.05, sigma=.2, T=.25)

def test_original_notebook_values():
    assert P.binomial(**A, N=100, kind="call") == pytest.approx(4.605026, abs=1e-5)
    assert P.binomial(**A, N=100, kind="put") == pytest.approx(3.362806, abs=1e-5)

def test_greeks_match_original():
    g = P.greeks(**A, N=100, kind="call")
    assert g["delta"] == pytest.approx(0.5693, abs=1e-4)
    assert g["vega"] == pytest.approx(19.62, abs=0.01)
    assert P.greeks(**A, N=100, kind="put")["delta"] == pytest.approx(-0.4307, abs=1e-4)

def test_american_tables():
    calls = [round(P.binomial(100, k, .05, .2, .25, 100, "call", True), 2) for k in (90, 95, 100, 105, 110)]
    puts = [round(P.binomial(100, k, .05, .2, .25, 100, "put", True), 2) for k in (90, 95, 100, 105, 110)]
    assert calls == [11.67, 7.72, 4.61, 2.49, 1.19]
    assert puts == [0.56, 1.58, 3.47, 6.43, 10.33]

def test_convergence_to_bs():
    bs = P.black_scholes(**A)
    assert abs(P.binomial(**A, N=500) - bs) < 5e-3
    assert abs(P.trinomial(**A, N=200) - bs) < 5e-3

def test_trinomial_put_and_american():
    assert P.trinomial(**A, N=200, kind="put", american=True) >= P.trinomial(**A, N=200, kind="put")

def test_parity():
    assert P.parity_check(**A, N=100)["holds"]
    assert P.parity_check(**A, N=100, american=True)["holds"]

def test_asian_below_european():
    a = P.asian_mc(**A, kind="put", n_paths=20000)
    assert a["price"] < P.black_scholes(**A, kind="put")
    assert a["price"] == pytest.approx(a["geometric"], abs=0.1)

def test_hedge_starts_flat_and_improves():
    r1, p1, _ = P.delta_hedge(100, 100, .05, .2, .25, 4, "call", seed=1, N=40)
    r2, p2, _ = P.delta_hedge(100, 100, .05, .2, .25, 64, "call", seed=1, N=40)
    assert abs(r1[0]["portfolio"]) < 1e-9 and abs(r2[0]["portfolio"]) < 1e-9
    assert abs(p2) < 1.0

def test_shapley_efficiency():
    base = dict(S0=110, K=100, r=.05, sigma=.3, T=.5); ref = dict(S0=100, K=100, r=.05, sigma=.2, T=.25)
    phi, v0, v1 = E.attribution(base, ref, "call", False, 30)
    assert sum(phi.values()) == pytest.approx(v1 - v0, abs=1e-9)

def test_assistant():
    assert "Delta" in E.ask("what is delta?")
