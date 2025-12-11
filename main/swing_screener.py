import pandas as pd
from datetime import datetime
import sqlite3

DB_PATH_DEL = "data\\delivery_highest.db"
DB_PATH_DEL_SP = "data\\delivery_spike.db"


def ema(data, length=20, price_col='CLOSE_PRICE'):
    if len(data) < length:
        data[f'EMA_{length}'] = pd.Series([None] * len(data))
        return data
    ema_col = f'EMA_{length}'
    data[ema_col] = data[price_col].ewm(span=length, adjust=False).mean()
    return data


def init_db_highest_del():
    conn = sqlite3.connect(DB_PATH_DEL)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS delivery_highest (
            SYMBOL TEXT,
            DATE TEXT,
            SIGNAL_DATE TEXT,
            CURRENT_DELIVERY_PERC REAL,
            PREV_HIGHEST_DELIVERY_PERC REAL,
            AVG_DELIVERY_PERC REAL,
            DELIVERY_SPIKE_RATIO_AVG REAL,
            HIGH_PRICE REAL,
            EMA REAL,
            CLOSE_ABOVE_EMA_HD TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("delivery_highest DB initialized.")


def save_to_highest_del(df):
    if df.empty:
        print("No records to save for highest delivery.")
        return
    conn = sqlite3.connect(DB_PATH_DEL)
    df.to_sql("delivery_highest", conn, if_exists="append", index=False)
    conn.close()


def init_db_del_spike():
    conn = sqlite3.connect(DB_PATH_DEL_SP)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS delivery_spike (
            SYMBOL TEXT,
            DATE TEXT,
            SIGNAL_DATE TEXT,
            CURRENT_DELIVERY_PERC REAL,
            PREV_DELIVERY_PERC REAL,
            AVG_DELIVERY_PERC REAL,
            DELIVERY_SPIKE_RATIO_PREV REAL,
            HIGH_PRICE REAL,
            EMA REAL,
            CLOSE_ABOVE_EMA_DS TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("delivery_spike DB initialized.")


def save_to_del_spike(df):
    if df.empty:
        print("No records to save for delivery spike.")
        return
    conn = sqlite3.connect(DB_PATH_DEL_SP)
    df.to_sql("delivery_spike", conn, if_exists="append", index=False)
    conn.close()


# 🔹 EMA integrated directly inside the scanner
def delivery_scanner(data, ema_length=20):
    result = []
    del_spike = []

    for symbol, group in data.groupby('SYMBOL'):
        group = group.sort_values('DATE1').reset_index(drop=True)
        group = ema(group, ema_length, price_col='CLOSE_PRICE')

        if len(group) < 14:
            print(f'{symbol}: Not enough data (needs ≥14 days)')
            continue

        signal_date = datetime.now().strftime('%Y-%m-%d')
        current_day = group.iloc[-1]
        prev_day = group.iloc[-2]
        past_14_days = group.iloc[-14:-1]

        prev_delivery = prev_day['DELIV_PER']
        current_delivery = current_day['DELIV_PER']
        avg_delivery_percent = past_14_days['DELIV_PER'].mean()
        highest_past_delivery = past_14_days['DELIV_PER'].max()

        current_ema = current_day.get(f'EMA_{ema_length}', None)
        close_price = current_day.get('CLOSE_PRICE', None)
        
        # handle None or NaN safely
        if pd.isna(current_ema) or pd.isna(close_price):
            CLOSE_ABOVE_EMA_HD = 'N'
            CLOSE_ABOVE_EMA_DS = 'N'
        else:
            CLOSE_ABOVE_EMA_HD = 'Y' if close_price > current_ema else 'N'
            CLOSE_ABOVE_EMA_DS = 'Y' if close_price > current_ema else 'N'

        # Condition 1: Current > Highest Past Delivery
        if current_delivery > highest_past_delivery:
            result.append({
                'SYMBOL': symbol,
                'DATE': current_day['DATE1'],
                'SIGNAL_DATE': signal_date,
                'CURRENT_DELIVERY_PERC': current_delivery,
                'PREV_HIGHEST_DELIVERY_PERC': highest_past_delivery,
                'AVG_DELIVERY_PERC': round(avg_delivery_percent, 2),
                'DELIVERY_SPIKE_RATIO_AVG': round(current_delivery / avg_delivery_percent, 2),
                'HIGH_PRICE': current_day['HIGH_PRICE'],
                'EMA': current_ema,
                'CLOSE_ABOVE_EMA_HD': CLOSE_ABOVE_EMA_HD
            })

        # Condition 2: Delivery Spike vs Previous Day
        if (current_delivery > prev_delivery) and (current_delivery > avg_delivery_percent):
            del_spike.append({
                'SYMBOL': symbol,
                'DATE': current_day['DATE1'],
                'SIGNAL_DATE': signal_date,
                'CURRENT_DELIVERY_PERC': current_delivery,
                'PREV_DELIVERY_PERC': prev_delivery,
                'AVG_DELIVERY_PERC': round(avg_delivery_percent, 2),
                'DELIVERY_SPIKE_RATIO_PREV': round((current_delivery - prev_delivery) / prev_delivery, 2),
                'HIGH_PRICE': current_day['HIGH_PRICE'],
                'EMA': current_ema,
                'CLOSE_ABOVE_EMA_DS': CLOSE_ABOVE_EMA_DS
            })

    return result, del_spike

def main():
    data = pd.read_csv(r"data\bhav_fo.csv")

    init_db_highest_del()
    init_db_del_spike()

    data = data[['SYMBOL', 'DATE1', 'OPEN_PRICE', 'HIGH_PRICE', 'LOW_PRICE', 'LAST_PRICE',
                 'CLOSE_PRICE', 'TTL_TRD_QNTY', 'TURNOVER_LACS', 'NO_OF_TRADES',
                 'DELIV_QTY', 'DELIV_PER']].sort_values(['SYMBOL', 'DATE1']).reset_index(drop=True)

    stocks, del_spike = delivery_scanner(data)

    stocks = pd.DataFrame(stocks).sort_values("DELIVERY_SPIKE_RATIO_AVG", ascending=False).reset_index(drop=True)
    del_spike = pd.DataFrame(del_spike).sort_values("DELIVERY_SPIKE_RATIO_PREV", ascending=False).reset_index(drop=True)

    save_to_highest_del(stocks)
    save_to_del_spike(del_spike)

if __name__ == "__main__":
    main()