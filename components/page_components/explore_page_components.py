# ----- Imports -----
import pandas as pd

import streamlit as st

import plotly.graph_objs as go

from helpers.data_manipulation_helpers import DataManipulationHelpers
from data.configs import STOCK_TICKERS_DICT

dmh__i = DataManipulationHelpers()

# ----- TradeSocial Explore Page Components -----

def generate_todays_top_gainers_section(
    gainers_list,
    ticker_df,
    gains_df,
    STOCK_TICKERS_DICT    
):
    """
    """
    st.markdown("## Today's Top Gainers")
    st.markdown('---')
    
    st.write(
        f"""
        The `Top Gainers` are those that have shown the most significant
        positive price movements over the recent period, indicating strong market performance.
        """
    )
    
    gain_rank = 1
    for ticker in gainers_list:
        company = STOCK_TICKERS_DICT[ticker]
        pct_gain = (
            round(list(gains_df[gains_df['ticker']==ticker]
            ['pct_change'])[0], 2)
        )
        
        line_color = 'green' if pct_gain >=0 else 'red'
        gain_sign = '+' if pct_gain >=0 else '-'
        
        history = ticker_df[ticker_df['ticker']==ticker][['Date', 'Close']]
        
        st.markdown(
            f"""### `#{gain_rank} {company} ({ticker}), {gain_sign}{pct_gain}%`
            """
        )
        
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=history['Date'],
                y=history['Close'],
                mode='lines',
                line=dict(color=line_color)
            )
        )
        fig.update_layout(
            title=f"{company} ({ticker})",
            xaxis_title='Date',
            yaxis_title='Price ($)'
        )
        st.plotly_chart(fig)
        gain_rank += 1