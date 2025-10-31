import pandas as pd
import numpy as np
import sqlite3

# Read CSVs
stocks_info = pd.read_csv(r'data\NFO_stocks.csv') 
data_w = pd.read_csv(r'data\stock_w.csv')
data_d = pd.read_csv(r'data\stock_d.csv')
DB_PATH = "data\\week_low_swing.db"

def init_db_week_low_swing():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS week_low_swing (
            symbol TEXT,
            signal_date TEXT,
            close REAL,
            prev_week_high REAL,
            week_end_date REAL
        )
    """)
    conn.commit()
    conn.close()
    print("week_low_swing DB initialized..")

def save_to_highest_del(df):
    if df.empty:
        print("No records to save..")
        return
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("week_low_swing", conn, if_exists="append", index=False)
    conn.close()        

def get_week():
    data_w['date'] = pd.to_datetime(data_w['date']).dt.date
    max_date = data_w['date'].max()
    weekday = max_date.weekday()
    print(f"Today: {weekday}")

    if weekday >= 4:
        print('inside if:')
        latest_date = data_w['date'].max()
        current_week = data_w[data_w['date'] == max_date]
        prev_weeks = data_w[data_w['date'] < max_date]
    else:
        print('inside else:')
        prev_data = data_w[data_w['date'] < max_date]
        latest_date = prev_data['date'].max()
        current_week = prev_data[prev_data['date'] == latest_date]
        prev_weeks = prev_data[prev_data['date'] < latest_date]

    print(f"current_week date: {latest_date}")
    print(f"prev_weeks date range: {prev_weeks['date'].min()} → {prev_weeks['date'].max()}")

    return current_week, prev_weeks


def week_analysis():
    current_week, prev_weeks = get_week()
    result = []

    for _, row in stocks_info.iterrows():
        symbol = row['symbol']
        curr = current_week[current_week['symbol'] == symbol]
        prev = prev_weeks[prev_weeks['symbol'] == symbol]

        if curr.empty or prev.empty:
            continue

        curr_low = curr['low'].values[0]
        prev_low_min = prev['low'].min()

        if curr_low < prev_low_min:
            result.append({
                'symbol': symbol,
                'high': curr['high'].values[0],
                'low': curr['low'].values[0],
                'current_week_low': curr_low,
                'prev_weeks_lowest_low': prev_low_min,
                'week_end_date': pd.to_datetime(curr['date'].values[0])
            })

    if not result:
        print("No stocks matching the weekly criteria.")
        return None
    #print(pd.DataFrame(result))
    return pd.DataFrame(result)


def day_analysis():
    df = week_analysis()
    if df is None or df.empty:
        print("No weekly matches found.")
        return []

    data_d['date'] = pd.to_datetime(data_d['date'])
    result = []

    for _, row in df.iterrows():
        s = row['symbol']
        week_end_date = row['week_end_date']
        prev_high = row['high']

        # Filter daily candles after the week-end date
        group = data_d[(data_d['symbol'] == s) & (data_d['date'] > week_end_date)]
        if group.empty:
            continue

        close_max = group['close'].max()
        if close_max > prev_high:
            signal_date = group[group['close'] == close_max]['date'].values[0]
            result.append({
                'symbol': s,
                'signal_date': signal_date,
                'close': close_max,
                'prev_week_high': prev_high,
                'week_end_date': week_end_date
            })

    if not result:
        print("No daily signals found after each weekly low.")
        return None
    else:
        result_df = pd.DataFrame(result)
        print(result_df)
        return result_df


if __name__ == '__main__':
    init_db_week_low_swing()
    df = day_analysis()

    if df is not None and not df.empty:
        conn = sqlite3.connect(DB_PATH)
        db_df = pd.read_sql_query("SELECT * FROM week_low_swing", conn)
        conn.close()

        db_df['signal_date'] = pd.to_datetime(db_df['signal_date'])
        df['signal_date'] = pd.to_datetime(df['signal_date'])
        new_df = df[~df['signal_date'].isin(db_df['signal_date'])] # we get signal dates which are not yet saved

        if not new_df.empty:
            save_to_highest_del(new_df)
        else:
            print("No new data to save.")