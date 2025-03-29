import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 Bitcoin Dashboard mit Technischer Analyse")

# Auswahlzeitraum
days = st.selectbox("Zeitraum wählen", [30, 90, 180], index=1)
interval = "1d"

# BTC-Daten abrufen
btc = yf.download("BTC-USD", period=f"{days}d", interval=interval)
btc.dropna(inplace=True)

# SMA
btc["SMA_20"] = btc["Close"].rolling(20).mean()
btc["SMA_50"] = btc["Close"].rolling(50).mean()

# Fibonacci-Level
high = btc["High"].max()
low = btc["Low"].min()
levels = {
    "0.0%": high,
    "23.6%": high - 0.236 * (high - low),
    "38.2%": high - 0.382 * (high - low),
    "50.0%": high - 0.5 * (high - low),
    "61.8%": high - 0.618 * (high - low),
    "78.6%": high - 0.786 * (high - low),
    "100.0%": low,
}

# RSI
delta = btc["Close"].diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = -delta.where(delta < 0, 0).rolling(14).mean()
rs = gain / loss
btc["RSI"] = 100 - (100 / (1 + rs))

# MACD
ema_12 = btc["Close"].ewm(span=12, adjust=False).mean()
ema_26 = btc["Close"].ewm(span=26, adjust=False).mean()
btc["MACD"] = ema_12 - ema_26
btc["Signal"] = btc["MACD"].ewm(span=9, adjust=False).mean()

# Signalindikator
last_rsi = btc["RSI"].iloc[-1]
last_macd = btc["MACD"].iloc[-1]
last_signal = btc["Signal"].iloc[-1]

st.subheader("📌 Aktuelle Signale")
if last_rsi < 30 and last_macd > last_signal:
    st.success(f"🚨 RSI = {round(last_rsi,2)} | MACD Buy-Signal erkannt")
elif last_rsi > 70:
    st.warning(f"⚠️ RSI = {round(last_rsi,2)} | Markt überhitzt")
else:
    st.info(f"RSI = {round(last_rsi,2)} | MACD = {round(last_macd,2)}")

# Charts anzeigen
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

# Kurs + SMA + Fibonacci
ax1.plot(btc.index, btc["Close"], label="BTC Close", linewidth=2)
ax1.plot(btc.index, btc["SMA_20"], label="SMA 20", linestyle="--")
ax1.plot(btc.index, btc["SMA_50"], label="SMA 50", linestyle="--")
for label, level in levels.items():
ax1.axhline(float(level), linestyle="--", alpha=0.4, label=f"Fib {label}")
ax1.set_ylabel("Preis (USD)")
ax1.legend()
ax1.grid(True)

# RSI
ax2.plot(btc.index, btc["RSI"], label="RSI", color="purple")
ax2.axhline(70, color="red", linestyle="--")
ax2.axhline(30, color="green", linestyle="--")
ax2.set_ylabel("RSI")
ax2.legend()
ax2.grid(True)

# MACD
ax3.plot(btc.index, btc["MACD"], label="MACD", color="blue")
ax3.plot(btc.index, btc["Signal"], label="Signal", color="orange", linestyle="--")
ax3.set_ylabel("MACD")
ax3.legend()
ax3.grid(True)

st.pyplot(fig)

