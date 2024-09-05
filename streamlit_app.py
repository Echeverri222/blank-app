import streamlit as st
import pandas as pd
import yfinance as yf
import math
from datetime import datetime
import plotly.express as px

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Stock Price Dashboard',
    page_icon=':chart_with_upwards_trend:',  # Stock emoji as icon
)

# -----------------------------------------------------------------------------
# Declare useful functions.

@st.cache_data
def get_stock_data(tickers, start_date, end_date):
    """Fetch stock price data from Yahoo Finance."""
    stock_data = yf.download(tickers, start=start_date, end=end_date)
    stock_data = stock_data['Adj Close']  # We only care about adjusted closing prices
    stock_data = stock_data.reset_index()  # Convert the index (Date) to a column
    return stock_data

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :chart_with_upwards_trend: Stock Price Dashboard

Track the price performance of your favorite stocks over a selected time range.
'''

# Add some spacing
''
''

# Date range slider
min_date = datetime(2010, 1, 1)
max_date = datetime.today()
start_date, end_date = st.slider(
    'Select the date range:',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# Select stock tickers
default_stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
tickers = st.text_input(
    'Enter stock tickers separated by commas:',
    ','.join(default_stocks)
)
selected_tickers = [ticker.strip().upper() for ticker in tickers.split(',')]

# Fetch stock price data
stock_data = get_stock_data(selected_tickers, start_date, end_date)

# Convert 'Date' column to datetime objects and remove timezone information
stock_data['Date'] = pd.to_datetime(stock_data['Date']).dt.tz_localize(None)

# Filter the data
filtered_stock_df = stock_data[
    (stock_data['Date'] >= pd.to_datetime(start_date))
    & (pd.to_datetime(end_date) >= stock_data['Date'])
]

# Show header
st.header('Stock Prices Over Time')

# Plot the stock prices using Plotly Express
fig = px.line(
    filtered_stock_df.melt(id_vars='Date', value_vars=selected_tickers, var_name='Ticker', value_name='Price'),
    x='Date',
    y='Price',
    color='Ticker',
    title='Stock Prices'
)

# Add chart to Streamlit
st.plotly_chart(fig)

# Display current stock prices and growth metrics
st.header(f'Stock Prices as of {end_date.date()}', divider='gray')

# Display metrics for each stock
cols = st.columns(4)
last_prices = stock_data[stock_data['Date'] == stock_data['Date'].max()]

for i, ticker in enumerate(selected_tickers):
    col = cols[i % len(cols)]
    
    with col:
        # Get first and last price
        first_price = stock_data[stock_data['Date'] == stock_data['Date'].min()][ticker].values[0]
        last_price = last_prices[ticker].values[0]

        # Calculate growth
        if math.isnan(first_price) or math.isnan(last_price):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_price / first_price:,.2f}x'
            delta_color = 'normal'

        # Show metrics in Streamlit
        st.metric(
            label=f'{ticker} Price',
            value=f'${last_price:,.2f}',
            delta=growth,
            delta_color=delta_color
        )
