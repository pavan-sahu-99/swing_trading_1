import plotly.graph_objects as go
import pandas as pd

def plot_stock_chart(symbol):
    df = pd.read_csv("data/stock_d.csv")
    df = df[df['symbol'] == symbol]
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df['date'], open=df['open'], high=df['high'],
                                 low=df['low'], close=df['close'], name='Price'))
    fig.update_layout(title=f"{symbol} - Price Chart", xaxis_rangeslider_visible=False)
    return fig
