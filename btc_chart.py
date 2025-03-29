import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests

# Daten laden
btc = yf.download("BTC-USD", period="90d", interval="1d")
btc.dropna(inplace=True)

# Fibonacci-Level berechnen
recent_high = btc['High'].max().item()
recent_low = btc['Low'].min().item()
fib_levels = {
    '0.0%': recent_high,
    '23.6%': recent_high - 0.236 * (recent_high - recent_low),
    '38.2%': recent_high - 0.382 * (recent_high - recent_low),
    '50.0%': recent_high - 0.5 * (recent_high - recent_low),
    '61.8%': recent_high - 0.618 * (recent_high - recent_low),
    '78.6%': recent_high - 0.786 * (recent_high - recent_low),
    '100.0%': recent_low
}

# Gleitende Durchschnitte
btc['SMA_20'] = btc['Close'].rolling(window=20).mean()
btc['SMA_50'] = btc['Close'].rolling(window=50).mean()

# RSI
delta = btc['Close'].diff()
gain = delta.where(delta > 0, 0).rolling(window=14).mean()
loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
rs = gain / loss
btc['RSI'] = 100 - (100 / (1 + rs))

# MACD
ema_12 = btc['Close'].ewm(span=12, adjust=False).mean()
ema_26 = btc['Close'].ewm(span=26, adjust=False).mean()
btc['MACD'] = ema_12 - ema_26
btc['Signal'] = btc['MACD'].ewm(span=9, adjust=False).mean()

# === Chart-Bereich ===
fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(14, 14), sharex=True,
                                         gridspec_kw={'height_ratios': [3, 1, 1, 1]})

# Plot 1: Preis mit SMA & Fibonacci
ax1.plot(btc.index, btc['Close'], label='BTC Close', linewidth=2)
ax1.plot(btc.index, btc['SMA_20'], label='SMA 20', linestyle='--')
ax1.plot(btc.index, btc['SMA_50'], label='SMA 50', linestyle='--')

colors = ['#FF6666', '#FF9966', '#FFCC66', '#66FF66', '#66CCCC', '#6699FF', '#9966FF']
for (label, level), color in zip(fib_levels.items(), colors):
    ax1.axhline(y=level, linestyle='--', alpha=0.6, linewidth=1.3, label=f'Fib {label}', color=color)

ax1.set_ylabel('Preis (USD)')
ax1.set_title('Bitcoin Kurs mit Fibonacci, SMA20/50')
ax1.legend()
ax1.grid(True)

# Plot 2: Volumen
vol = btc['Volume'] / 1e9
ax2.plot(btc.index, vol, color='gray', alpha=0.5, label='Volumen')
ax2.set_ylabel('Volumen (Mrd.)')
ax2.set_title('Handelsvolumen')
ax2.grid(True)

# Plot 3: RSI
ax3.plot(btc.index, btc['RSI'], label='RSI', color='purple')
ax3.axhline(70, color='red', linestyle='--')
ax3.axhline(30, color='green', linestyle='--')
ax3.set_ylabel('RSI')
ax3.set_title('Relative Strength Index (14)')
ax3.grid(True)
ax3.legend()

# Plot 4: MACD
ax4.plot(btc.index, btc['MACD'], label='MACD', color='blue')
ax4.plot(btc.index, btc['Signal'], label='Signal', color='orange', linestyle='--')
ax4.set_ylabel('MACD')
ax4.set_title('MACD & Signal')
ax4.legend()
ax4.grid(True)

plt.tight_layout()

# Speichern des Charts als Bild
chart_path = "btc_chart.png"
plt.savefig(chart_path)

# Mail versenden
from send_email import send_email_with_chart

subject = "📊 BTC Chart & Signal"
last_rsi = btc['RSI'].iloc[-1]
last_macd = btc['MACD'].iloc[-1]
last_signal = btc['Signal'].iloc[-1]
message = f"Aktueller BTC Chart\nRSI: {round(last_rsi, 2)}\nMACD: {round(last_macd, 2)} / Signal: {round(last_signal, 2)}"

send_email_with_chart(subject, message, chart_path)

# Chart anzeigen
plt.show()


# === Pushover Benachrichtigung ===
def send_push(title, message):
    payload = {
        "token": "a6j4gfjcyrws98iuifn12smynshz4u",
        "user": "u7kj5ztwew1p2dybb8p4asmt6g7m5v",
        "title": title,
        "message": message
    }
    requests.post("https://api.pushover.net/1/messages.json", data=payload)

# Aktuelle Signale prüfen
last_rsi = btc['RSI'].iloc[-1]
last_macd = btc['MACD'].iloc[-1]
last_signal = btc['Signal'].iloc[-1]

alert_msg = ""

if last_rsi < 30 and last_macd > last_signal:
    alert_msg += "🚨 RSI < 30 & MACD-Kaufsignal\n"
if last_rsi > 70:
    alert_msg += "⚠️ RSI > 70 – Markt überkauft\n"
if last_macd > last_signal and (last_macd - last_signal) > 50:
    alert_msg += "📈 Starker MACD-Schub\n"

if alert_msg:
    send_push("📊 BTC-Alarm", alert_msg)
    print("✅ Push-Benachrichtigung gesendet.")
else:
    print("ℹ️ Kein Alarm – Markt neutral.")




