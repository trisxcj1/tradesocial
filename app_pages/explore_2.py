# ----- Imports -----
import pandas as pd

import streamlit as st
import yfinance as yf

import plotly.graph_objs as go

from helpers.data_manipulation_helpers import DataManipulationHelpers
from data.configs import STOCK_TICKERS_DICT

from components.page_components.explore_page_components import (
    explore_test
)

dmh__i = DataManipulationHelpers()

# ----- TradeSocial Explore Page TEST -----
def generate_explore_2():
    st.markdown("# Explore TEST")
    explore_test()
    st.write(
        f"""
        Welcome to the Explore Page! Use this page to stay informed about
        market trends and spot potential investment opportunities.
        """
    )
    stock_tickers = list(STOCK_TICKERS_DICT.keys())
    stock_tickers.sort()
    
    st.write("## Browse and Compare Stocks")
    st.markdown('---')
    stocks_to_view = st.multiselect('Search Stocks', stock_tickers)
    
    # search and compare
    if stocks_to_view:
        st.markdown("YEAH THIS WORKS FOR NOW")
    else:
        gainers_rank_to_filter = 5
        stocks_df = pd.DataFrame(
            columns=['Date', 'Close', 'ticker']
        )
        
        for ticker in stock_tickers:
            ticker_df = dmh__i.get_ystock_data_over_time(ticker)
            ticker_df.reset_index(inplace=True)
            ticker_df.rename(columns={'index': 'Date'}, inplace=True)
            ticker_df = ticker_df[['Date', 'Close', 'ticker']]
            stocks_df = pd.concat([stocks_df, ticker_df], ignore_index=True)
        
        gains = dmh__i.calculate_percentage_gain(stocks_df)
        gains['rank'] = gains['pct_change'].rank(method='dense', ascending=False)
        
        top_gainers_list = (
            list(gains
            .sort_values('rank', ascending=True)
            .head(gainers_rank_to_filter)
            ['ticker'])
        )
        st.markdown(top_gainers_list)
            