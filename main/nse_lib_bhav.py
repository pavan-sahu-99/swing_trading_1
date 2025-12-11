from nselib import capital_market as cm
from datetime import timedelta, datetime
import pandas as pd

def get_data():
    to_date = datetime.now().date()
    from_date = to_date - timedelta(30)

    print(f"Fetching data from {from_date} to {to_date}")
    bhav_consolidated = pd.DataFrame()

    current_day = from_date
    while current_day <= to_date:
        try:
            date_str = current_day.strftime('%d-%m-%Y')
            print(f"Fetching data for: {date_str}")

            bhav = cm.bhav_copy_with_delivery(date_str)
            print(f"Data fetched for {date_str}")                

            bhav_consolidated = pd.concat([bhav_consolidated, bhav], ignore_index=True)

        except Exception as e:
            print(f"Error fetching data for {date_str}: {e}")

        current_day += timedelta(days=1)
    return bhav_consolidated


def main():
    bhav_consolidated = get_data()
    bhav_fo = pd.DataFrame()
    data = pd.read_csv(r'data\NFO_stocks.csv')
    symbols = data['symbol'].to_list()
    if not bhav_consolidated.empty:
        bhav_consolidated = bhav_consolidated[bhav_consolidated['SERIES'] == 'EQ'].sort_values(['SYMBOL', 'DATE1'], ascending=True).reset_index(drop=True)
        print(bhav_consolidated.head())
        bhav_consolidated.drop_duplicates(inplace=True)
        bhav_consolidated['DATE1'] = pd.to_datetime(bhav_consolidated['DATE1'], format='%d-%b-%Y')
        bhav_consolidated.to_csv(r'data\bhav_consolidated.csv')    
        bhav_fo = bhav_consolidated[bhav_consolidated['SYMBOL'].isin(symbols)]
        
        # for sym in symbols:
        #     if sym in bhav_consolidated['SYMBOL'].unique():
        #         bhav_fo = pd.concat([bhav_fo, bhav_consolidated[bhav_consolidated['SYMBOL'] == sym]], ignore_index=True)
        bhav_fo = bhav_fo[['SYMBOL', 'DATE1', 'OPEN_PRICE', 'HIGH_PRICE', 'LOW_PRICE', 'LAST_PRICE', 'CLOSE_PRICE', 'TTL_TRD_QNTY', 'TURNOVER_LACS', 'NO_OF_TRADES', 'DELIV_QTY', 'DELIV_PER']].sort_values(['SYMBOL', 'DATE1'], ascending=True).reset_index(drop=True)
        bhav_fo.to_csv(r'data\bhav_fo.csv')
    else:
        print("No data was fetched successfully.")

if __name__ == '__main__':
    main()