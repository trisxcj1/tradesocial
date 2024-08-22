# ----- Imports -----
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import streamlit as st

import yaml
from yaml.loader import SafeLoader
import os
from dotenv import load_dotenv

import plotly.graph_objs as go
import plotly.express as px

from helpers.data_manipulation_helpers import DataManipulationHelpers
from helpers.llm_helpers import LLMHelpers
from helpers.plotting_helpers import PlottingHelpers
from data.configs import STOCK_TICKERS_DICT
from app_secrets.current_user_config import (
    USER_RISK_LEVEL
)

load_dotenv()
users_config_path = os.getenv('USERS_CONFIG_LOCATION')
current_user_config_path = os.getenv('CURRENT_USERS_CONFIG_LOCATION')

dmh__i = DataManipulationHelpers()
llmh__i = LLMHelpers()
ph__i = PlottingHelpers()

# ----- TradeSocial Explore Page Components -----
with open(users_config_path) as file:
    users_config = yaml.load(file, Loader=SafeLoader)
users_info = users_config['credentials']['usernames']
stock_association_rules = dmh__i.gen_association_rules()

fy_recommendations = dmh__i.claculate_fy_recommended_stocks(USER_RISK_LEVEL)['recommended_stocks']
fy_quick_recommendations = dmh__i.claculate_fy_recommended_stocks(USER_RISK_LEVEL, quick_fy=True)['recommended_stocks']

fy_buys = list(fy_recommendations['buys']['ticker'])
fy_sells = list(fy_recommendations['sells']['ticker'])
fy_quick_buys = list(fy_quick_recommendations['buys']['ticker'])
fy_quick_sells = list(fy_quick_recommendations['sells']['ticker'])

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

def string_format_big_number(num):
    if num < 1000:
        return str(num)
    elif num >= 1000 and num < 1000000:
        return f"{num/1000:.1f}K"
    elif num >= 1000000 and num < 1000000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000000000:
        return f"{num/1000000000:.1f}B"

def calculate_portfolio_metrics(portfolio):
    portfolio_value_df = pd.DataFrame(
        columns=['ticker', 'quantity', 'initial_price', 'initial_value', 'current_price', 'current_value']
    )
    
    for ticker in portfolio:
        for transaction in portfolio[ticker]:
            transaction_date = transaction['transaction_date']
            transaction_date_d = datetime.strptime(transaction_date, '%Y-%m-%d').date()
            transaction_date_end = (transaction_date_d + relativedelta(days=1)).strftime('%Y-%m-%d')
            
            initial_stock_data = dmh__i.get_ystock_data_over_time(
                ticker,
                transaction_date,
                transaction_date_end
            )
            initial_stock_data = initial_stock_data[['ticker', 'Close']]
            initial_stock_data.rename(columns={'Close': 'initial_price'}, inplace=True)
            initial_stock_data['quantity_i'] = transaction['quantity'] 
            initial_stock_data['initial_value'] = initial_stock_data['quantity_i'] * initial_stock_data['initial_price']
            
            current_stock_data = dmh__i.get_ystock_data_over_time(
                ticker,
                start_date='most recent trading day'
            )
            current_stock_data = current_stock_data[['ticker', 'Close']]
            current_stock_data.rename(columns={'Close': 'current_price'}, inplace=True)
            current_stock_data['quantity'] = transaction['quantity']
            current_stock_data['current_value'] = current_stock_data['quantity'] * current_stock_data['current_price']
            
            joined_data = (
                initial_stock_data
                .merge(current_stock_data, on='ticker', how='inner')
            )
            joined_data = joined_data.drop('quantity_i', axis=1)
            portfolio_value_df = pd.concat([portfolio_value_df, joined_data], ignore_index=True)
    
    portfolio_value_df = dmh__i.calculate_portfolio_value(portfolio_value_df)
    return portfolio_value_df

def generate_best_portfolio_combinations_section():
    """
    """
    odf = pd.DataFrame(columns=['portfolio_stocks', 'pct_change'])
    # for username in list(users_info.keys()):
    for username in ['tj', 'techbro', 'stonksonlygoup']:
        current_df = pd.DataFrame(columns=['portfolio_stocks', 'pct_change'])
        portfolio = users_info[username]['portfolio']
        if len(portfolio) > 0:
            portfolio_stocks = list(users_info[username]['portfolio'].keys())
            portfolio_value_df = calculate_portfolio_metrics(portfolio)
            portfolio_value_df = (
                portfolio_value_df[portfolio_value_df['current_value']>0]    
            )
            
            initial_portfolio_value = (
                portfolio_value_df
                ['avg_initial_value']
                .sum()
            )
            current_portfolio_value = (
                portfolio_value_df
                ['current_value']
                .sum()
            )
            if initial_portfolio_value > 0:
                portfolio_pct_change = 0.0
            else:
                portfolio_pct_change = (
                    round(100 * (current_portfolio_value - initial_portfolio_value)/initial_portfolio_value, 2)
                )
            current_df['portfolio_stocks'] = portfolio_stocks
            current_df['pct_change'] = portfolio_pct_change
            odf = pd.concat([odf, current_df], ignore_index=True)
    odf['rank'] = odf['pct_change'].rank(method='dense', ascending=False)
    odf = odf.sort_values('rank', ascending=True)
    # return odf
    st.write(odf)
    
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
        The **Top Gainers** are those that have shown the most significant
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
    
    trending_df = trending_df.drop_duplicates(subset='ticker')
    trending_df['rank'] = trending_df['Volume'].rank(method='dense', ascending=False)
    trending_stocks = list(
        trending_df[trending_df['rank']<11]
        # trending_df
        .sort_values('rank', ascending=True)
        ['ticker']
    )
    
    st.markdown("## Trending 🔥")
    st.markdown('---')
    st.markdown(
        f"""
        Stay on top of market movements with **Trending**.
        
        Here are the stocks that had the highest traded volume over the previous day.
        These stocks are currently attracting significant attention in the market,
        making them worth watching for potential investment opportunities.
        """
    )
    
    trending_placeholder_1 = st.empty()
    trending_placeholder_2 = st.empty()
    
    with trending_placeholder_1.container():
        columns_1 = st.columns(5)
        for i, ticker in enumerate(trending_stocks[:5]):
            df = trending_df[trending_df['ticker']==ticker]
            ticker_volume = list(df['Volume'])[0]
            columns_1[i].metric(
                label=f"{ticker}",
                value=f"{string_format_big_number(ticker_volume)}",
                delta=None
            )
            
    with trending_placeholder_2.container():
        columns_2 = st.columns(5)
        for i, ticker in enumerate(trending_stocks[5:]):
            df = trending_df[trending_df['ticker']==ticker]
            ticker_volume = list(df['Volume'])[0]
            columns_2[i].metric(
                label=f"{ticker}",
                value=f"{string_format_big_number(ticker_volume)}",
                delta=None
            )
    

def generate_popular_portfolio_stocks_section():
    """
    """
    popular_stocks_dict = {}
    for username in list(users_info.keys()):
        for ticker in list(users_info[username]['portfolio'].keys()):
            user_total_ticker_quantity = 0
            for i in range(len(users_info[username]['portfolio'][ticker])):
                user_total_ticker_quantity += users_info[username]['portfolio'][ticker][i]['quantity']
            if ticker in list(popular_stocks_dict.keys()):
                popular_stocks_dict[ticker] = popular_stocks_dict[ticker] + user_total_ticker_quantity
            else:
                popular_stocks_dict[ticker] = user_total_ticker_quantity
    
    popular_stocks_df = pd.DataFrame(list(popular_stocks_dict.items()), columns=['ticker', 'quantity'])
    popular_stocks_df = popular_stocks_df.sort_values('quantity', ascending=False).head(5)
    
    st.markdown("## Popular Portfolio Stocks Right Now")
    st.markdown("---")
    st.markdown(
        f"""
        Discover stocks that other investors are holding in their portfolios!
        
        **Popular Portfolio Stocks Right Now** represents the stocks with the largest quantity
        that TradeSocial investors are holding in their portfolios right now, measured by the
        number of units of Shares in Portfolios.
        
        By seeing what others are investing in, you can gain insights into market trends
        and explore potential investment opportunities.
        """
    )
    popular_portfolio_stocks_placeholder = st.empty()
    with popular_portfolio_stocks_placeholder.container():
        columns = st.columns(5)
        
        for i, ticker in enumerate(list(popular_stocks_df['ticker'])):
            quantity = list(popular_stocks_df[popular_stocks_df['ticker']==ticker]['quantity'])[0]
            
            columns[i].metric(
                label=f"{ticker}",
                value=f"{string_format_big_number(quantity)}",
                delta=None
            )
        

def generate_technical_graphs_section(
    stock_df,
    ticker
):
    """
    """
    st.markdown("### Technical Graphs")
    st.markdown('---')
    
    possible_metrics = ['Moving Average', 'MACD', 'RSI', 'Bollinger Bands']
    metrics = st.multiselect('Select a Metric', possible_metrics, default=possible_metrics)
    odf = stock_df[['Date', 'Close']].sort_values('Date', ascending=True).tail(500)
    odf.rename(columns={'Close': 'value'}, inplace=True)
    odf['label'] = ['Actual Price'] * len(odf)
    avg_stock_price = stock_df['Close'].mean()
    
    # Moving Avg section
    if 'Moving Average' in metrics:
        st.markdown("#### Moving Average")
        st.markdown(
            f"""
            **Moving Averages (MAs)** are popular indicators that smooth out price information to help
            identify trends over a specified period. These averages help investors understand the direction
            and strength of a stock's trend by filtering out short-term price fluctuations.
            
            When short-term MAs cross above long-term MAs, it signals that there is a potential upward trend,
            which suggests a `buying opportunity` for stocks. When short-term MAs cross below long-term MAs, however,
            it signals a potential downward trend which could indicate a potential `selling opportunity`.
            
            Using MAs, in conjunction with other indicators and your investment strategy, can help you
            make more informed trading decisions and improve your investment outcomes.
            """
        )
        ma_periods = st.slider('Select Moving Average Periods', min_value=7, max_value=250, value=[7, 100], step=1)
        for period in ma_periods:
            ma_df = stock_df[['Date', 'Close']].sort_values('Date', ascending=True).tail(500)
            ma_df['value'] = ma_df['Close'].rolling(window=period).mean()
            ma_df = ma_df[['Date', 'value']].dropna()
            ma_df['label'] = [f"{period}-Day MA"] * len(ma_df)
            odf = pd.concat([odf, ma_df], ignore_index=True)
            
        fig = px.line(
            odf,
            x='Date',
            y='value',
            color='label',
            title=f"{ticker} Moving Average Analysis",
            labels={
                'value': 'Price ($)',
                'label': 'Label'
            }
        )
        st.plotly_chart(fig)
    
    # MACD section
    if 'MACD' in metrics:
        st.markdown("#### Moving Average Convergence Divergence (MACD)")
        st.markdown(
            f"""
            The **Moving Average Convergence Divergence (MACD)** is a momentum indicator that is
            typically used to identify changes in the strength, direction, and duration of a stock's
            price trend. 
            
            The `MACD Line` represents the difference between the exponential moving averages of the
            fast and slow periods. The significance of the `Fast Period` is that it responds more quickly
            to recent price changes. This means that it is more sensitive to recent price movements and
            captures short-term trends and momentum effectively. The `Slow Period`, however, smooths out
            the stock price over time. This makes it less sensitive to recent price fluctuations,
            which helps it capture broader, long-term trends.
            
            The `Signal Line` is an exponential moving average of the `MACD Line`. When the `MACD Line`
            crosses above the `Signal Line`, it suggests that the recent momentum is stronger that the
            long-term trend, which might indicate a `buying opportunity`. However, when the `MACD Line`
            crosses below the `Signal Line`, it indicates that the recent momentum is weaker compared to 
            the longer-term trend, which might suggest a `selling opportunity`. 
            
            Lastly, when looking at the `MACD Histogram`, positive values indicate that the fast period
            is gaining on the slow period, once again indicating potential `buying opportunities`.
            
            Using MACD, in conjunction with other indicators and your investment strategy, can help you
            make more informed trading decisions and improve your investment outcomes.
            """
        )
        macd_signal_period = st.slider('Select The MACD Signal Period', min_value=7, max_value=250, value=9, step=1)
        macd_fast_period = st.slider('Select The MACD Fast Period', min_value=7, value=12, max_value=250, step=1)
        macd_slow_period = st.slider('Select The MACD Slow Period', min_value=7, value=26, max_value=250, step=1)
        
        macd_df = dmh__i.calculate_macd(
            stock_df[['Date', 'Close']],
            macd_signal_period,
            macd_fast_period,
            macd_slow_period
        )
        macd_df = macd_df.tail(macd_slow_period + 60)
        
        macd_fig = go.Figure()
        macd_fig.add_trace(
            go.Scatter(
                x=macd_df['Date'],
                y=macd_df['macd_line'],
                mode='lines',
                name='MACD Line',
                line=dict(color='blue')
            )
        )
        macd_fig.add_trace(
            go.Scatter(
                x=macd_df['Date'],
                y=macd_df['macd_signal'],
                mode='lines',
                name='MACD Signal',
                line=dict(color='red')
            )
        )
        macd_fig.add_trace(
            go.Bar(
                x=macd_df['Date'],
                y=macd_df['macd_hist'],
                name='MACD Histogram',
                marker_color='lightgreen'
            )
        )
        macd_fig.update_layout(
            title=f"{ticker} MACD Analysis",
            xaxis_title='Date',
            yaxis_title='Value'
        )
        st.plotly_chart(macd_fig)
        
    # RSI section    
    if 'RSI' in metrics:
        st.markdown("#### Relative Strength Index (RSI)")
        st.markdown(
            f"""
            The **Relative Strength Index (RSI)** is a momentum oscillator that measures the speed
            and change of price movements to identify overbought or oversold conditions in a stock.
            
            The `RSI` value ranges from 0 to 100, and is typically calculated using a 14-day period.
            This value helps gauge the strength of recent price movements and whether a stock is
            potentially overbought or oversold.
            
            An `Overbought` scenario is when the price of a stock has risen significantly and rapidly,
            pushing the stock's value to levels that might not be sustainable in the short term. Typically,
            a stock is considered overbought when the RSI value increases to 70 or above. An overbought
            stock might be due for a price correction or price decline as market conditions normalize.
            Therefore, as an investor, you can use this signal to `consider selling or taking profits`.
            
           An `Oversold` scenario is when the price of a stock has dropped significantly and rapidly, resulting
           in levels that might be undervalued in the short term. Typically, a stock is considered oversold
           when the RSI value decreases to 30 or below. An oversold stock might be poised for for a price
           rebound or increase as the market normalizes. Therefore, as an investor, you can use this signal
           to `consider buying a stock`.
            
            Using RSI, in conjunction with other indicators and your investment strategy, can help you
            make more informed trading decisions and improve your investment outcomes.
            """
        )
        rsi_period = st.slider('Select RSI Period', min_value=7, max_value=250, value=14, step=1)
        rsi_overbought_level = st.slider('Select Overbought Level', min_value=0, value=70, max_value=100, step=1)
        rsi_oversold_level = st.slider('Select Oversold Level', min_value=0, value=30, max_value=100, step=1)
        
        rsi_df = dmh__i.calculate_rsi(stock_df[['Date', 'Close']], rsi_period)
        rsi_df = rsi_df[['Date', 'RSI']].tail(rsi_period + 60)
        
        rsi_fig = go.Figure()
        rsi_fig.add_trace(
            go.Scatter(
                x=rsi_df['Date'],
                y=rsi_df['RSI'],
                mode='lines',
                name=f"{rsi_period}-Day RSI"
            )
        )
        rsi_fig.add_trace(
            go.Scatter(
                x=rsi_df['Date'],
                y=[rsi_overbought_level] * len(rsi_df),
                mode='lines',
                name=f"Overbought Level",
                line=dict(color='red', width=1, dash='dash')
            )
        )
        rsi_fig.add_trace(
            go.Scatter(
                x=rsi_df['Date'],
                y=[rsi_oversold_level] * len(rsi_df),
                mode='lines',
                name=f"Oversold Level",
                line=dict(color='green', width=1, dash='dash')
            )
        )
        rsi_fig.add_trace(
            go.Scatter(
                x=rsi_df['Date'].to_list() + rsi_df['Date'][::-1].to_list(),
                y=[rsi_overbought_level] * len(rsi_df) + [rsi_oversold_level] * len(rsi_df),
                fill='toself',
                fillcolor='rgba(144, 238, 144, 0.4)',
                name=f"Valid Range",
                line=dict(color='rgba(144, 238, 144, 0)')
            )
        )
        rsi_fig.update_layout(
            title=f"{ticker} Relative Strength Index Analysis",
            xaxis=dict(title='Date'),
            yaxis=dict(title='RSI'),
        )
        st.plotly_chart(rsi_fig)
    
    if 'Bollinger Bands' in metrics:
        st.markdown("#### Bollinger Bands")
        st.markdown(
            """
            **Bollinger Bands** help gaugue the volatility of a stock, which is
            represented by the distance between the upper and lower bands on the graph.
            A wider band indicates `higher volatility`, while a narrorwer band suggests 
            `lower volatility`.
            
            When the stock price approaches the `Upper Band`, the stock is typically thought
            to be overbought and could be due for a price correction. Therefore, as an investor,
            you can use this signal to `consider selling or taking profits`.
            
            When the price approaches the `Lower Band`, the stock is typically thought
            to be oversold and could be due for a price rebound. Therefore, as an investor,
            you can use this signal to `consider a buying opportunity`.
            
            This visualization helps you to quickly gauge the current volatility and potential
            price levels of the stock, assisting in making more informed trading decisions.
            """
        )
        bollinger_period = st.slider('Select The Moving Average Period', min_value=7, max_value=250, value=20, step=1)
        bollinger_n_stddevs = st.slider('Select The Number of Standard Deviations', min_value=1, value=2, max_value=5, step=1)
        
        bollinger_df = dmh__i.calculate_bollinger_bands(stock_df[['Date', 'Close']], bollinger_period, bollinger_n_stddevs)
        bollinger_df = bollinger_df[['Date', 'ma_line', 'upper_band', 'lower_band']].tail(bollinger_period + 60)
        
        bollinger_fig = go.Figure()
        bollinger_fig.add_trace(
            go.Scatter(
                x=bollinger_df['Date'],
                y=bollinger_df['ma_line'],
                mode='lines',
                name=f"{bollinger_period}-Day MA"
            )
        )
        bollinger_fig.add_trace(
            go.Scatter(
                x=bollinger_df['Date'],
                y=bollinger_df['upper_band'],
                mode='lines',
                name=f"Upper Band",
                line=dict(color='red')
            )
        )
        bollinger_fig.add_trace(
            go.Scatter(
                x=bollinger_df['Date'],
                y=bollinger_df['lower_band'],
                mode='lines',
                name=f"Lower Band",
                line=dict(color='green')
            )
        )
        bollinger_fig.add_trace(
            go.Scatter(
                x=pd.concat([bollinger_df['Date'], bollinger_df['Date'][::-1]]),
                y=pd.concat([bollinger_df['upper_band'], bollinger_df['lower_band'][::-1]]),
                fill='toself',
                fillcolor='rgba(144, 238, 144, 0.4)',
                name=f"Valid Range",
                line=dict(color='rgba(144, 238, 144, 0)')
            )
        )
        bollinger_fig.update_layout(
            title=f"{ticker} Bollinger Band Analysis",
            xaxis=dict(title='Date'),
            yaxis=dict(title='Price ($)'),
        )
        st.plotly_chart(bollinger_fig)

    
    
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
    
    if len(stocks_to_view)==1:
        # if in buys, can be in quick_buys or quick_sells
        if (stocks_to_view[0] in fy_buys) and (stocks_to_view[0] in fy_quick_buys):
            st.markdown("`Predicted to increase in the short-term and over the next few months`")
        elif (stocks_to_view[0] in fy_buys) and (stocks_to_view[0] in fy_quick_sells):
            st.markdown("`Predicted to decrease in the short-term, but increase within the next few months`")
        
        # if in quick_buys, can be in buys or sells
        elif (stocks_to_view[0] in fy_quick_buys) and (stocks_to_view[0] in fy_sells):
            st.markdown("`Predicted to increase in the short-term, but decrease within the next few months`")
            
        # if in sells, can be in quick_buys or quick_sells
        elif (stocks_to_view[0] in fy_sells) and (stocks_to_view[0] in fy_quick_sells):
            st.markdown("`Predicted to decrease in the short-term and over the next few months`")
        
        else:
            st.write(f"Quick buy: {stocks_to_view[0] in fy_quick_buys}, {fy_quick_buys}")
            st.write(f"Quick sell: {stocks_to_view[0] in fy_quick_sells}, {fy_quick_sells}")
            st.write(f"Overall buy: {stocks_to_view[0] in fy_buys}, {fy_buys}")
            st.write(f"Overall sell: {stocks_to_view[0] in fy_sells}, {fy_sells}")
        
        # plotting time series decomp
        if len(stocks_df) >= 504:
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
        
        # showing advanced technical charts
        show_technical_graphs = st.toggle('Show Advanced Technical Graphs', key='ShowTechnicalGraphsToggle_on_Explore')
        if show_technical_graphs:
            generate_technical_graphs_section(stocks_df, stocks_to_view[0])
        
        # investors who have ticker_x also have ticker_y
        investors_also_have = dmh__i.gen_investors_also_bought(stock_association_rules, stocks_to_view[0])
        if investors_also_have is not None:
            consequent = investors_also_have.iloc[0]['consequents']
            consequent_str = ' + '.join(list(consequent))
            
            st.write("### Investors Also Have")
            st.write("---")
            st.write(f"TradeSocial investors who have `{stocks_to_view[0]}` in their portfolio also have ```{consequent_str}```")
        
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
    # for ticker in stocks_to_view:
    #     recent_news_df = pd.concat([recent_news_df, llmh__i.get_recent_news(ticker, 5)])
    # if len(recent_news_df) > 0:
    #     st.markdown("### Recent News")
    #     st.markdown('---')
    #     for ticker in stocks_to_view:
    #         if len(recent_news_df[recent_news_df['ticker']==ticker]) > 0:
    #             st.markdown(f"#### `{STOCK_TICKERS_DICT[ticker]} ({ticker})`:")
    #             headlines = recent_news_df[recent_news_df['ticker']==ticker]['headline']
    #             urls = recent_news_df[recent_news_df['ticker']==ticker]['url']
    #             articles = recent_news_df[recent_news_df['ticker']==ticker]['body']
                
    #             # info_to_summarize = "\n\n".join(
    #             #     [
    #             #         f"{headline}\n\n{body}" for headline, body in zip(headlines, articles)
    #             #     ]
    #             # )
    #             info_to_summarize = f"{headlines[0]}\n\n{articles[0]}"
    #             summary = llmh__i.summarize_articles(info_to_summarize)
                
    #             st.markdown('> **Summary ✨**')
    #             st.write(f"> **`{summary}`**")
                
    #             for i in range(len(headlines)):
    #                 st.text(f"Headline: {headlines[i]}")
    #                 st.markdown(f"- Click [here to read more]({urls[i]})")
    
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
