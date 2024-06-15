# ----- Imports -----
import pandas as pd

import streamlit as st
import yfinance as yf

import plotly.graph_objs as go

from helpers.data_manipulation_helpers import DataManipulationHelpers
from data.configs import STOCK_TICKERS_DICT

from components.page_components.explore_page_components import generate_todays_top_gainers_section

dmh__i = DataManipulationHelpers()

# ----- TradeSocial Explore Page -----
def generate_explore_page():
    """
    """
    st.markdown("# Explore")
    
    st.write(
        f"""
        Welcome to the Explore Page! Use this page to stay informed about
        market trends and spot potential investment opportunities.
        """
    )
    
    gainers_rank_to_filter = 5
    stock_tickers = list(STOCK_TICKERS_DICT.keys())
    
    stocks_df = pd.DataFrame(
        columns=['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'ticker']
    )
    
    for ticker in stock_tickers[:10]:
        ticker_df = dmh__i.get_ystock_data_over_time(ticker)
        ticker_df.reset_index(inplace=True)
        ticker_df.rename(columns={'index': 'Date'}, inplace=True)
        stocks_df = pd.concat([stocks_df, ticker_df], ignore_index=True)
    
    
    gains = dmh__i.calculate_percentage_gain(stocks_df)
    gains['rank'] = gains['pct_change'].rank(method='dense', ascending=False)
    
    top_gainers_list = (
        list(gains
        .sort_values('rank', ascending=True)
        .head(gainers_rank_to_filter)
        ['ticker'])
    )
    top_losers_list = (
        list(gains
        .sort_values('rank', ascending=False)
        .head(gainers_rank_to_filter)
        ['ticker'])
    )
    
    # Today's Top Gainers
    generate_todays_top_gainers_section(
        top_gainers_list,
        stocks_df,
        gains,
        STOCK_TICKERS_DICT
    )
    
    
    
    