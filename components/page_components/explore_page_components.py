# ----- Imports -----
import pandas as pd

import streamlit as st

import plotly.graph_objs as go
import plotly.express as px

from helpers.data_manipulation_helpers import DataManipulationHelpers
from helpers.llm_helpers import LLMHelpers
from data.configs import STOCK_TICKERS_DICT

dmh__i = DataManipulationHelpers()
llmh__i = LLMHelpers()

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

def generate_trending_section(
    STOCK_TICKERS_DICT
):
    """
    """
    all_stocks = list(STOCK_TICKERS_DICT.keys())
    trending_df = pd.DataFrame(
        columns=['Date', 'Volume', 'ticker']
    )
    
    for ticker in all_stocks:
        ticker_df = dmh__i.get_ystock_data_over_time(
            ticker,
            start_date='most recent trading day'
        )
        ticker_df.reset_index(inplace=True)
        ticker_df.rename(columns={'index': 'Date'}, inplace=True)
        ticker_df = ticker_df[['Date', 'Volume', 'ticker']]
        trending_df = pd.concat([trending_df, ticker_df], ignore_index=True)
    
    trending_df['rank'] = trending_df['Volume'].rank(method='dense', ascending=False)
    trending_socks = list(
        trending_df[trending_df['rank']<6]
        ['ticker']
    )
    
    st.markdown("## Trending 🔥")
    st.markdown('---')
    trend_rank = 1
    for stock in trending_socks:
        st.write(f"#### `#{trend_rank} {STOCK_TICKERS_DICT[stock]} ({stock})`")
        trend_rank += 1
    

def generate_browse_and_compare_section(
    stocks_to_view
):
    """
    """
    st.markdown("### Performance Over Time")
    
    stocks_df = pd.DataFrame(
        columns=['Date', 'Close', 'ticker']
    )
    recent_news_df = pd.DataFrame()
    
    for ticker in stocks_to_view:
        ticker_df = dmh__i.get_ystock_data_over_time(ticker)
        ticker_df.reset_index(inplace=True)
        ticker_df.rename(columns={'index': 'Date'}, inplace=True)
        ticker_df = ticker_df[['Date', 'Close', 'ticker']]
        stocks_df = pd.concat([stocks_df, ticker_df], ignore_index=True)
        recent_news_df = pd.concat([recent_news_df, llmh__i.get_recent_news(ticker, 3)])
        
    
    # performance over time
    fig = px.line(
        stocks_df,
        x='Date',
        y='Close',
        color='ticker',
        title='Stock Price Over Time',
        labels={
            'Close': 'Price ($)',
            'ticker': 'Stock'
        }
    )
    st.plotly_chart(fig)
    
    # recent news 
    if len(recent_news_df) > 0:
        st.markdown("### Recent News")
        st.markdown('---')
        for ticker in stocks_to_view:
            st.markdown(f"#### `{STOCK_TICKERS_DICT[ticker]} ({ticker})`:")
            headlines = recent_news_df[recent_news_df['ticker']==ticker]['headline']
            urls = recent_news_df[recent_news_df['ticker']==ticker]['url']
            for i in range(len(headlines)):
                st.text(f"Headline: {headlines[i]}")
                st.markdown(f"- Click [here to read more]({urls[i]})")
    
    # more like this
    st.markdown("### More Like This")
    st.markdown('---')
    
    all_similarities_df = dmh__i.calculate_similarity()
    more_like_this = []
    
    for ticker in stocks_to_view:
        similar_stocks = list(all_similarities_df[ticker].sort_values(ascending=False).index[1:4])
        more_like_this = more_like_this + similar_stocks
    
    more_like_this = list(dict.fromkeys(more_like_this))
    more_like_this = [x for x in more_like_this if x not in stocks_to_view]
    
    for s in more_like_this:
        st.write(f"#### `{STOCK_TICKERS_DICT[s]} ({s})`")
        