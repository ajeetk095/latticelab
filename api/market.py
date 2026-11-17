"""Free, key-less market data: Yahoo Finance (via yfinance) with cache + graceful fallback to demo mode;
US Treasury 13-week bill (^IRX) as risk-free proxy."""
from __future__ import annotations
import numpy as np
import pandas as pd
import streamlit as st


@st.cache_data(ttl=300, show_spinner=False)
def get_history(ticker: str, period: str = "6mo"):
    """Returns (DataFrame|None, error|None)."""
    try:
        import yfinance as yf
        df = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        if df is None or df.empty:
            return None, "No data returned (market closed, bad ticker, or rate-limit)."
        df = df.reset_index()
        df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
        return df, None
    except Exception as e:  # network blocked, etc.
        return None, f"{type(e).__name__}: {e}"


@st.cache_data(ttl=3600, show_spinner=False)
def get_risk_free():
    df, err = get_history("^IRX", "5d")
    if df is None:
        return None, err
    return float(df["Close"].iloc[-1]) / 100, None


def demo_history(S0=100.0, sigma=0.25, days=126, seed=11):
    """Deterministic synthetic GBM series used when live data is unavailable."""
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0003, sigma / np.sqrt(252), days)
    px = S0 * np.exp(np.cumsum(r))
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=days)
    return pd.DataFrame({"Date": dates, "Close": px})


def realised_vol(df, window=30):
    r = np.log(df["Close"]).diff().dropna()
    return float(r.tail(window).std() * np.sqrt(252))
