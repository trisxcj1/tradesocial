# ----- Imports -----
import pandas as pd

import streamlit as st
import yfinance as yf

import plotly.graph_objs as go

from helpers.data_manipulation_helpers import DataManipulationHelpers
from data.configs import STOCK_TICKERS_DICT

from components.page_components.explore_page_components import (
    generate_todays_top_gainers_section,
    generate_trending_section,
    generate_browse_and_compare_section
)

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
    stock_tickers = list(STOCK_TICKERS_DICT.keys())
    stock_tickers.sort()
    
    st.write("## Browse and Compare Stocks")
    st.markdown('---')
    stocks_to_view = st.multiselect('Search Stocks', stock_tickers)
    
    # search and compare
    if stocks_to_view:
        generate_browse_and_compare_section(
            stocks_to_view
        )
    
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
        
        # Trending now
        generate_trending_section(STOCK_TICKERS_DICT)
    
    
    
    