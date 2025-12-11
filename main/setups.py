import pandas as pd
import numpy as np
import sqlite3
import talib as ta

db_path_del_highest = "data//bullish_stocks.db"
db_path_del_spike = "data//del_bullish_stocks.db"
kite_data = "data//stock_d.csv"


def read_db_del_highest():
    conn = sqlite3.connect(db_path_del_highest)
    df = pd.read_sql_query(
        "SELECT * FROM bullish_stocks WHERE SIGNAL_DATE = (SELECT MAX(SIGNAL_DATE) FROM bullish_stocks)", 
        conn
    )
    conn.close()
    return df

def read_db_del_spike():
    conn = sqlite3.connect(db_path_del_spike)
    df = pd.read_sql_query(
        "SELECT * FROM del_bullish_stocks WHERE SIGNAL_DATE = (SELECT MAX(SIGNAL_DATE) FROM del_bullish_stocks)", 
        conn
    )
    conn.close()
    return df

def del_highest():
    data = pd.read_csv(r"data\bhav_fo.csv")
    df = read_db_del_highest()

    data = data[['SYMBOL', 'DATE1', 'TURNOVER_LACS']]
    data['DATE1'] = pd.to_datetime(data['DATE1'])

    data = data.sort_values(by=['SYMBOL', 'DATE1'])

    data['turnover_avg'] = (
        data.groupby('SYMBOL')['TURNOVER_LACS']
            .rolling(window=10)
            .mean()
            .reset_index(0, drop=True)
    )
    data['turnover_ratio'] = (data['TURNOVER_LACS'] / data['turnover_avg']).round(2)

    latest_df = data[data['DATE1'] == data['DATE1'].max()]
    latest_df = latest_df[['SYMBOL', 'turnover_ratio']]

    merged_df = pd.merge(df, latest_df, on='SYMBOL', how='inner')

    print("\nMerged DB + Turnover results:")
    print(merged_df[merged_df['turnover_ratio'] > 1.5])

    return merged_df

def del_spike():
    data = pd.read_csv(r"data\bhav_fo.csv")
    df = read_db_del_spike()

    data = data[['SYMBOL', 'DATE1', 'TURNOVER_LACS']]
    data['DATE1'] = pd.to_datetime(data['DATE1'])

    data = data.sort_values(by=['SYMBOL', 'DATE1'])

    data['turnover_avg'] = (
        data.groupby('SYMBOL')['TURNOVER_LACS']
            .rolling(window=10)
            .mean()
            .reset_index(0, drop=True)
    )
    data['turnover_ratio'] = (data['TURNOVER_LACS'] / data['turnover_avg']).round(2)

    latest_df = data[data['DATE1'] == data['DATE1'].max()]
    latest_df = latest_df[['SYMBOL', 'turnover_ratio']]

    merged_df = pd.merge(df, latest_df, on='SYMBOL', how='inner')
    merged_df = merged_df.rename(columns = {'SYMBOL':'symbol'})

    return merged_df

def atr_expansion(kite_data):
    data = pd.read_csv(kite_data)
    data = data.sort_values(['symbol', 'date'])
    data['atr'] = data.groupby('symbol').apply(
        lambda x: ta.ATR(x['high'], x['low'], x['close'], timeperiod=14)
    ).reset_index(level=0, drop=True)
    data['atr_avg'] = data.groupby('symbol')['atr'].rolling(20).mean().reset_index(level=0, drop=True)
    data['atr_ratio'] = data['atr'] / data['atr_avg']
    latest = data.groupby('symbol').tail(1)
    latest = latest[['symbol','instrument_token','atr','atr_avg','atr_ratio','date']]
    return latest


def historical_vol(kite_data, short_period=10, long_period=30):
    df = pd.read_csv(kite_data)
    df = df.sort_values(['symbol', 'date'])
    df['returns'] = df.groupby('symbol')['close'].apply(
        lambda x: np.log(x / x.shift(1))
    ).reset_index(level=0, drop=True)
    df['HV_10'] = df.groupby('symbol')['returns'].rolling(short_period).std().reset_index(level=0, drop=True)
    df['HV_10'] = df['HV_10'] * np.sqrt(252)
    df['HV_30'] = df.groupby('symbol')['returns'].rolling(long_period).std().reset_index(level=0, drop=True)
    df['HV_30'] = df['HV_30'] * np.sqrt(252)
    df['HV_ratio'] = df['HV_10'] / df['HV_30']
    df = df.groupby('symbol').tail(1)
    df = df[['symbol','instrument_token','HV_10','HV_30','HV_ratio','date']]
    return df

if __name__ == "__main__":
    hv = historical_vol(kite_data)
    atr = atr_expansion(kite_data)
    del_spike = del_spike()
    df = pd.merge(hv, atr, on=['symbol','instrument_token','date'])
    #print(df[df['symbol'] == 'CGPOWER'])
    df = pd.merge(df, del_spike, on=['symbol'],how = 'inner')
    filtered_df = df[(df['HV_ratio'] > 1) & (df['turnover_ratio'] > 1.2)]
    filtered_df = filtered_df[['symbol','atr_ratio','HV_ratio','CURRENT_DELIVERY_PERC','AVG_DELIVERY_PERC','turnover_ratio','SIGNAL_DATE']]
    #print(filtered_df.columns)
    filtered_df.to_csv("data\\filtered_df.csv", index=False)
    print(filtered_df)
