import sqlite3
import pandas as pd
import numpy as np

DB_PATH_DEL = r"data\delivery_spike.db"
DB_PATH_BULLISH = r"data\del_bullish_stocks.db"
CSV_PATH = r"data\stock_d.csv"

def init_db_bullish_stocks():
    conn = sqlite3.connect(DB_PATH_BULLISH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS del_bullish_stocks (
            SYMBOL TEXT,
            SIGNAL_DATE TEXT,
            CURRENT_DELIVERY_PERC REAL,
            AVG_DELIVERY_PERC REAL,
            DELIVERY_SPIKE_RATIO_PREV REAL
        )
    """)
    conn.commit()
    conn.close()
    print("del_bullish_stocks DB initialized.")

def save_to_bullish_stocks(df):
    conn = sqlite3.connect(DB_PATH_BULLISH)
    df.to_sql("del_bullish_stocks", conn, if_exists="append", index=False)
    conn.close()
    print(f"Saved {len(df)} records to del_bullish_stocks.")

def read_db_highest_del():
    conn = sqlite3.connect(DB_PATH_DEL)
    df = pd.read_sql_query("SELECT * FROM delivery_spike", conn)
    conn.close()
    return df

def main_function():
    # Read from database
    df = read_db_highest_del()

    # Read CSV data
    data = pd.read_csv(CSV_PATH)

    '''
    delivery_highest columns:
    ['SYMBOL', 'DATE', 'SIGNAL_DATE', 'CURRENT_DELIVERY_PERC',
     'PREV_HIGHEST_DELIVERY_PERC', 'AVG_DELIVERY_PERC',
     'DELIVERY_SPIKE_RATIO_AVG', 'HIGH_PRICE', 'EMA', 'CLOSE_ABOVE_EMA_DS']
    '''

    # Find the most recent signal date
    max_date = df['SIGNAL_DATE'].max()

    # Filter both datasets by that date
    df_del_today = df[df["SIGNAL_DATE"] == max_date]
    data_today = data[data['date'] == max_date]

    # Filter by symbols that appeared in delivery spike list
    symbols = df_del_today['SYMBOL'].unique()
    data_result = data_today[data_today['symbol'].isin(symbols)]

    # Merge both datasets
    df_final = data_result.merge(df_del_today, left_on='symbol', right_on='SYMBOL', how='inner')
    print(df_final.columns)
    '''
    Index(['Unnamed: 0', 'symbol', 'instrument_token', 'date', 'open', 'high',
       'low', 'close', 'volume', ]
    '''
    df_final = df_final[['SYMBOL', 'SIGNAL_DATE',
       'CURRENT_DELIVERY_PERC', 'PREV_DELIVERY_PERC',
       'AVG_DELIVERY_PERC', 'DELIVERY_SPIKE_RATIO_PREV', 'EMA',
       'CLOSE_ABOVE_EMA_DS', 'open', 'high', 'low', 'close', 'volume']]
    df_final.rename(columns={
        'open': 'OPEN',
        'high': 'HIGH',
        'low': 'LOW',
        'close': 'CLOSE',
        'volume': 'VOLUME'
    }, inplace=True)
    df_final['CANDLE'] = np.where(df_final['CLOSE'] > df_final['OPEN'], 'BULLISH',
                                  np.where(df_final['CLOSE'] < df_final['OPEN'], 'BEARISH', 'DOJI'))
    bullish_stocks = df_final[df_final['CANDLE']=='BULLISH']
    bullish_stocks = bullish_stocks[['SYMBOL', 'SIGNAL_DATE','CURRENT_DELIVERY_PERC','AVG_DELIVERY_PERC', 'DELIVERY_SPIKE_RATIO_PREV']].reset_index(drop=True)
    return bullish_stocks

def main():
    init_db_bullish_stocks()

    conn = sqlite3.connect(DB_PATH_BULLISH)
    last_date_df = pd.read_sql_query("SELECT MAX(SIGNAL_DATE) AS last_date FROM del_bullish_stocks", conn)
    conn.close()

    last_date = last_date_df.iloc[0, 0] if not last_date_df.empty else None

    bullish_stocks = main_function()
    print(bullish_stocks)

    max_date = bullish_stocks['SIGNAL_DATE'].max()
    if last_date is not None and pd.to_datetime(last_date) >= pd.to_datetime(max_date):
        print("No new bullish stocks to add.")
    else:
        save_to_bullish_stocks(bullish_stocks)
        print(f"Bullish stocks for {max_date} saved to database.")

if __name__ == "__main__":
    main()
