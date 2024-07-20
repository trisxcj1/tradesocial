# ----- Imports -----
import pandas as pd
from datetime import datetime
import streamlit as st

import plotly.graph_objs as go
import plotly.express as px

from helpers.data_manipulation_helpers import DataManipulationHelpers
from helpers.llm_helpers import LLMHelpers
from helpers.plotting_helpers import PlottingHelpers
from data.configs import STOCK_TICKERS_DICT

dmh__i = DataManipulationHelpers()
llmh__i = LLMHelpers()
ph__i = PlottingHelpers()

# ----- TradeSocial Explore Page Components -----
today = datetime.today()
months_mapping = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}

def generate_todays_top_gainers_section(
    gainers_list,
    ticker_df,
    gains_df,
    STOCK_TICKERS_DICT    
):
    """
    """
    st.markdown("## Yesterday's Top Gainers")
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
        ticker_df = dmh__i.get_ystock_data_over_time(ticker, start_date='2020-06-10')
        ticker_df.reset_index(inplace=True)
        ticker_df.rename(columns={'index': 'Date'}, inplace=True)
        ticker_df = ticker_df[['Date', 'Close', 'ticker']]
        stocks_df = pd.concat([stocks_df, ticker_df], ignore_index=True)
        recent_news_df = pd.concat([recent_news_df, llmh__i.get_recent_news(ticker, 5)])
    
    if len(stocks_to_view)==1:
        # plotting time series decomp
        stock_ts_decomp = dmh__i.calculate_ts_decomposition(stocks_df, stocks_to_view[0])
        st.plotly_chart(ph__i.plot_stock_decomposition(stock_ts_decomp, stocks_to_view[0]))
        
        cycle_information = dmh__i.generate_sesonality_information(stock_ts_decomp)
        typical_peak_month, typical_trough_month = cycle_information['typical_peak_month'], cycle_information['typical_trough_month']
        
        typical_peak_month_whole = int(typical_peak_month)
        typical_peak_month_remainder = typical_peak_month - typical_peak_month_whole
        
        typical_trough_month_whole = int(typical_trough_month)
        typical_trough_month_remainder = typical_trough_month - typical_trough_month_whole
        
        current_month = today.month
        high_month_before_low_month = typical_peak_month < typical_trough_month
        
        if typical_peak_month_remainder <= 0.25:
            when_is_peak_period_occurring = "Early"
        elif (typical_peak_month_remainder > 0.25) and (typical_peak_month_remainder < 0.75):
            when_is_peak_period_occurring = "Mid"
        else:
            when_is_peak_period_occurring = "Late"
            
        if typical_trough_month_remainder <= 0.25:
            when_is_trough_period_occurring = "Early"
        elif (typical_trough_month_remainder > 0.25) and (typical_trough_month_remainder < 0.75):
            when_is_trough_period_occurring = "Mid"
        else:
            when_is_trough_period_occurring = "Late"
        
        # good times to buy
        if (high_month_before_low_month) and ((current_month < typical_peak_month) or (current_month > typical_trough_month)):
            if current_month < typical_peak_month:    
                st.write(
                    f"""
                    Based on `{stocks_to_view[0]}`'s cyclical pattern, now could be a good time to `buy or long` the stock.
                    {STOCK_TICKERS_DICT[stocks_to_view[0]]}'s stock price has not yet reached its estimated peak period
                    for this year, which means that value of the stock is expected to increase. 
                    
                    Therefore, if you `buy or long`
                    `{stocks_to_view[0]}` today or before {when_is_peak_period_occurring}-{months_mapping[typical_peak_month_whole]},
                    you should expect to the value of your portfolio to increase over time while you own the stock.
                    """
                )
            if current_month > typical_trough_month:    
                st.write(
                    f"""
                    Based on `{stocks_to_view[0]}`'s cyclical pattern, now could be a good time to `buy or long` the stock.
                    {STOCK_TICKERS_DICT[stocks_to_view[0]]}'s stock price has already passed its estimated low period
                    for this year, which means that value of the stock is expected to increase. 
                    
                    Therefore, if you `buy or long`
                    `{stocks_to_view[0]}` today or before {when_is_peak_period_occurring}-{months_mapping[typical_peak_month_whole]},
                    you should expect to the value of your portfolio to increase over time while you own the stock.
                    """
                )
        if (~high_month_before_low_month) and ((current_month > typical_trough_month) and (current_month < typical_peak_month)):
            st.write(
                f"""
                Based on `{stocks_to_view[0]}`'s cyclical pattern, now could be a good time to `buy or long` the stock.
                {STOCK_TICKERS_DICT[stocks_to_view[0]]}'s stock price has already passed its estimated low period for the year,
                which means that the value of the stock is expected to increase.
                
                Therefore, if you `buy or long`
                `{stocks_to_view[0]}` today or before {when_is_peak_period_occurring}-{months_mapping[typical_peak_month_whole]},
                you should expect the value of your portfolio to increase over time while you own the stock.
                """
            )
                
        # good times to sell         
        if (high_month_before_low_month) and ((current_month > typical_peak_month) and (current_month < typical_trough_month)):
            st.write(
                f"""
                Based on `{stocks_to_view[0]}`'s cyclical pattern, now could be a good time to `sell or short` the stock.
                {STOCK_TICKERS_DICT[stocks_to_view[0]]}'s stock price has already passed its estimated peak period
                for this year and is approaching it's estimated low period, which means that value of the stock is
                expected to decrease.
                
                Therefore, if you `sell or short`
                `{stocks_to_view[0]}` today or before {when_is_trough_period_occurring}-{months_mapping[typical_trough_month_whole]},
                you should expect to the minimize any losses you might incur from owning this stock, and the value of your portfolio would
                at least remain the same or even increase.
                """
            )
    
        if (~high_month_before_low_month) and ((current_month < typical_trough_month) or (current_month > typical_peak_month)):
            if current_month < typical_trough_month:
                st.write(
                    f"""
                    Based on `{stocks_to_view[0]}`'s cyclical pattern, now could be a good time to `sell or short` the stock.
                    {STOCK_TICKERS_DICT[stocks_to_view[0]]}'s stock price has not yet reached its estimated low period
                    for this year, which means that value of the stock is expected to decrease.
                    
                    Therefore, if you `sell or short`
                    `{stocks_to_view[0]}` today or before {when_is_trough_period_occurring}-{months_mapping[typical_trough_month_whole]},
                    you should expect to the minimize any losses you might incur from owning this stock,
                    and the value of your portfolio would at least remain the same or even increase over time.
                    """
                )
            if current_month > typical_peak_month:
                st.write(
                    f"""
                    Based on `{stocks_to_view[0]}`'s cyclical pattern, now could be a good time to `sell or short` the stock.
                    {STOCK_TICKERS_DICT[stocks_to_view[0]]}'s stock price has already passed its estimated peak period
                    for this year, which means that value of the stock is expected to decrease.
                    
                    Therefore, if you `sell or short`
                    `{stocks_to_view[0]}` today or before {when_is_trough_period_occurring}-{months_mapping[typical_trough_month_whole]},
                    you should expect to the minimize any losses you might incur from owning this stock, 
                    and the value of your portfolio would at least remain the same or even increase over time.
                    """
                )
            
        st.write(
            f"""
            > The estimated peak period is {when_is_peak_period_occurring}-{months_mapping[typical_peak_month_whole]},
            and the estimated low period is {when_is_trough_period_occurring}-{months_mapping[typical_trough_month_whole]}
            """
        )
        
    else:
        # plotting performance over time
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
            articles = recent_news_df[recent_news_df['ticker']==ticker]['body']
            
            info_to_summarize = "\n\n".join([f"#### {headline}\n\n{body}" for headline, body in zip(headlines, articles)])
            summary = llmh__i.summarize_articles(info_to_summarize)
            
            st.markdown('> ***Summary ✨***')
            st.write(f"`{summary}`")
            
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
