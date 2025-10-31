## Swing Trading Reversal Strategy (`swing_trading_1`)

This project implements a **basic swing trading reversal strategy** using weekly and daily OHLC data for F&O stocks.

---

## Overview
The strategy identifies potential swing reversal opportunities based on **weekly lows and daily breakouts**.

We focus primarily on **F&O stocks** because:
- They are market movers with high liquidity.
- They allow both **cash and options trading**.
- Their price action is clean and reliable for technical setups.

You can easily extend this to include **equity stocks** as well.

---

## 🧠 Strategy Logic

1. **Weekly Setup Detection**
   - Fetch weekly OHLC data for all stocks.
   - Check if the **current week's low** is the **lowest among the last 7 weeks**.
   - Exclude stocks in a **long-term downtrend**.

2. **Daily Confirmation**
   - Wait for the **daily close** to move **above the previous week's high**.
   - That triggers a **buy entry** signal.

3. **Risk Management**
   - **Stop Loss (SL):** Low of that week.
   - **Target:** 2 × Risk (Risk–Reward ratio = 1:2).

---

## Tech Stack
- **Python Modules:**
  - `pandas` – for data handling  
  - `numpy` – for numeric operations  
  - `sqlite3` – for storing swing signal data  
  - *(Optional: `nselib` for fetching live NSE data)*

---

## Project Structure
swing_trading_1/
│
├── data/
│ ├── NFO_stocks.csv # List of tradable F&O symbols
│ ├── stock_w.csv # Weekly OHLC data
│ ├── stock_d.csv # Daily OHLC data
│ └── week_low_swing.db # SQLite database storing detected swing signals
│
├── main.py # Core logic for weekly + daily swing analysis
└── README.md

---
##  How to Run
# Clone the repo
git clone https://github.com/<your-username>/swing_trading_1.git
cd swing_trading_1

# Install dependencies
pip install pandas numpy nselib

---
## Example Output
    symbol     signal_date    close    prev_week_high
0   SUPREMEIND  2025-08-22     4637.8      4212.5
1   GLENMARK    2025-07-29     2158.0      1879.2

---
## Database Integration
swing/data/week_low_swing.db

---
## Future Additions
- Trend detection using EMA filters
- Telegram bot integration for signal alerts
- Backtesting report module
- Streamlit dashboard for visualization
---
