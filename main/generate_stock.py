from kiteconnect import KiteConnect
import pandas as pd
from datetime import datetime, timedelta
import time

last_request_time = 0
def rate_limited_call():
    global last_request_time
    min_interval = 0.35  
    now = time.time()
    wait_time = min_interval - (now - last_request_time)
    if wait_time > 0:
        time.sleep(wait_time)
    last_request_time = time.time()

def gen_ses():
    key = open(r"data\api.txt","r").read().split()
    kite = KiteConnect(api_key=key[0])
    kite.set_access_token(key[2])
    return kite

def get_data(kite, row, interval):
    try:
        to_date = datetime.now()
        from_date = to_date - timedelta(days=100)
        data = kite.historical_data(int(row['instrument_token']), from_date, to_date, interval)
        df = pd.DataFrame(data)
        df["symbol"] = row['symbol']
        df["instrument_token"] = row['instrument_token']
        df["interval"] = interval
        df = df[['symbol','instrument_token', 'date', 'open', 'high', 'low', 'close', 'volume']]
        return df
    except Exception as e:
        print(f"Error for {row['symbol']} - {interval}: {e}")
        return pd.DataFrame()
    
if __name__ == "__main__":
    kite = gen_ses()
    print("Kite Session Generated")
    stock_df = pd.read_csv(r"data\NFO_stocks.csv") 
    df_d = pd.DataFrame()
    df_w = pd.DataFrame()
    total_stocks = len(stock_df)
    for i, row in stock_df.iterrows():
        df_d = pd.concat([df_d, get_data(kite, row, "day")], ignore_index=True)
        rate_limited_call()
        df_w = pd.concat([df_w, get_data(kite, row, "week")], ignore_index=True)
        print(f"Processing {i+1}/{total_stocks}: {row['symbol']}")
    
    df_d['date'] = pd.to_datetime(df_d['date']).dt.date
    df_d.to_csv(r"data\stock_d.csv")
    print("df_d csv saved ...")
    df_w['date'] = pd.to_datetime(df_w['date']).dt.date
    df_w.to_csv(r"data\stock_w.csv")
    print("df_w csv saved ...")