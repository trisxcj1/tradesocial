# ----- Imports -----
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

import os
from dotenv import load_dotenv

import yaml
from yaml.loader import SafeLoader

import streamlit as st

import plotly.graph_objs as go
import plotly.express as px

from helpers.data_manipulation_helpers import DataManipulationHelpers
from data.configs import (
    STOCK_TICKERS_DICT
)
from app_secrets.current_user_config import (
    USER_USERNAME,
    USER_PORTFOLIO,
    USER_RISK_LEVEL
)

dmh__i = DataManipulationHelpers()

load_dotenv()
users_config_path = os.getenv('USERS_CONFIG_LOCATION')
current_user_config_path = os.getenv('CURRENT_USERS_CONFIG_LOCATION')

# ----- TradeSocial Home Page Components -----
portfolio = USER_PORTFOLIO
fy_recommendations = dmh__i.claculate_fy_recommended_stocks(USER_RISK_LEVEL)['recommended_stocks'] # risk level is not currently being used
ymal_recommendation_dict = dmh__i.calculate_ymal_recommended_stocks(USER_RISK_LEVEL)


# TODO: move to data manipulation helpers
def calculate_my_portfolio_metrics_over_time(portfolio=portfolio):
    
    portfolio_value_df = pd.DataFrame(
        columns=['Date', 'ticker', 'Close', 'quantity_owned']
    )
    
    for ticker in portfolio:
        ticker_df = pd.DataFrame(
            columns=['Date', 'ticker', 'Close', 'quantity_owned']
        )
        
        for transaction in portfolio[ticker]:
            transaction_date = transaction['transaction_date']
            stock_data = dmh__i.get_ystock_data_over_time(
                ticker,
                transaction_date
            )
            stock_data.reset_index(inplace=True)
            stock_data.rename(columns={'index': 'Date'}, inplace=True)
            stock_data = stock_data[['Date', 'ticker', 'Close']]
            stock_data['quantity_owned'] = [transaction['quantity']] * len(stock_data)
            
            ticker_df = pd.concat([ticker_df, stock_data], ignore_index=True)
            
            # need to agg by date to account for additional stock purchased
            ticker_df = (
                ticker_df
                .groupby(['Date', 'ticker', 'Close'])
                .agg(
                    quantity_owned = pd.NamedAgg('quantity_owned', 'sum')
                )
                .reset_index()
                .sort_values('Date', ascending=False)
            )
            
        portfolio_value_df = pd.concat([portfolio_value_df, ticker_df], ignore_index=True)
    
    portfolio_value_df['current_value'] = portfolio_value_df['quantity_owned'] * portfolio_value_df['Close']
    return portfolio_value_df
       
def calculate_my_portfolio_metrics(portfolio=portfolio):
    # portfolio = current_user_info['portfolio']
    
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

def generate_my_portfolio_section():
    """
    """
    st.markdown("### My Portfolio Value")
    
    portfolio_over_time = calculate_my_portfolio_metrics_over_time()
    
    if len(portfolio_over_time) > 0:
    
        portfolio_value_df = calculate_my_portfolio_metrics()
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
        portfolio_pct_change = (
            round(100 * (current_portfolio_value - initial_portfolio_value)/initial_portfolio_value, 2)
        )

        gain_sign = '+' if portfolio_pct_change >=0 else '-'

        st.markdown(f"### Current Portfolio Value: ${current_portfolio_value:,.2f} ({gain_sign}{portfolio_pct_change}%)")
        
        portfolio_agg_level = st.toggle('Show Portfolio Distribution', key='ShowPortfolioDistribution_on_Home')
        show_distribution = True if portfolio_agg_level else False
        
        if show_distribution:
            fig = px.pie(
                values=portfolio_value_df['current_value'],
                names=portfolio_value_df['ticker'],
                title=f"Breakdown of Current Portfolio Value"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            fig = px.line(
                portfolio_over_time,
                x='Date',
                y='current_value',
                color='ticker',
                title=f"My Portfolio Over Time",
                labels={
                    'current_value': 'Value ($)',
                    'ticker': 'Stock Ticker'
                }
            )
            st.plotly_chart(fig)
    else:
        st.warning('Buy shares in a stock to grow your portfolio! Check out the Explore Page.')

def generate_update_my_portfolio_section():
    st.markdown("### Update My Portfolio")
    stock_association_rules = dmh__i.gen_association_rules()
    
    st.error(
        f"""
        **NOTE**: TradeSocial currently does not have the functionality to support the actual
        buying or selling of securities.
        
        TradeSocial currently allows you to log your trading activity and then generates
        personalized insights based on your activity, interests, goals, and industry trends.
        
        Use TradeSocial to enhance your trading strategy and discover new investment opportunities
        just for you 😎.
        """
    )
    
    portfolo_update_counter = 0 
    with st.form(key=f'update_portfolio_form_on_home_{portfolo_update_counter}'):
        available_tickers = list(STOCK_TICKERS_DICT.keys())
        ticker = st.selectbox('Ticker', available_tickers)
        quantity = st.number_input('Quantity', min_value=1)
        transaction_date = st.date_input('Transaction Date', min_value=datetime(2000, 1, 1))
        transaction_type = st.selectbox('Transaction Type', ['Buy', 'Sell'])
        submit_button = st.form_submit_button(label='Update Portfolio')
        
        investors_also_bought = dmh__i.gen_investors_also_bought(
            stock_association_rules,
            ticker
        )
        
        if submit_button:
            portfolo_update_counter += 1
            if transaction_type == 'Sell':
                quantity = -quantity
                st.success(f"Sold {ticker}!")
            else:
                st.success(f"Purchased {ticker}!")
                if investors_also_bought is not None:
                    consequent = investors_also_bought.iloc[0]['consequents']
                    consequent_str = ' + '.join(list(consequent))
                    st.write(f"TradeSocial investors purchased `{ticker}` also purchased ```{consequent_str}```")
                
            if ticker in portfolio:
                portfolio[ticker].append({'quantity': quantity, 'transaction_date': transaction_date.strftime('%Y-%m-%d')})
            else:
                portfolio[ticker] = [{'quantity': quantity, 'transaction_date': transaction_date.strftime('%Y-%m-%d')}]
            
            with open(current_user_config_path, 'w') as current_user_py_file:
                current_user_py_file.write(f"USER_USERNAME = '{USER_USERNAME}'\n")
                current_user_py_file.write(f"USER_PORTFOLIO = {portfolio}\n")
                current_user_py_file.write(f"USER_RISK_LEVEL = {USER_RISK_LEVEL}")
            
            
            with open(users_config_path) as file:
                users_config = yaml.load(file, Loader=SafeLoader)
            users_config['credentials']['usernames'][USER_USERNAME]['portfolio'] = portfolio
            
            with open(users_config_path, 'w') as file:
                yaml.dump(users_config, file, default_flow_style=False)
            
            

def generate_fy_section(
    fy_buys=True
    # should also be based on risk level or something
):
    """
    """
    stocks_in_my_portfolio = list(portfolio.keys())
    if fy_buys:
        section_header = 'Recommended Buys For You'
        fy_msg = """
        Based on your interests and current industry trends, here are a few
        recommended buys for you!
        
        If you purchase these stocks today and 
        hold them for at least 3 months, the value of your portfolio is 
        expected to increase 🚀
        """
        fy = fy_recommendations['buys']
        
    else:
        section_header = 'Strategic Shorts or Sells'
        fy_msg = """
        The following stocks are expected to lose value within the next 3 months.
        
        If you short or sell these stocks today, you can minimize the risk of
        any losses you might incur from owning these stocks.
        """
        fy = fy_recommendations['sells']
        
    st.markdown(f"## {section_header}")
    st.markdown('---')
    
    st.write(fy_msg)
    
    # deduplicating for stocks that will be in YMAL
    stocks_in_ymal = ymal_recommendation_dict['recommended_stocks']
    recommended_stocks = list(
        fy[~fy['ticker'].isin(stocks_in_ymal)]
        .head(4)
        ['ticker']
    )
    fy_placeholder = st.empty()
    with fy_placeholder.container():
        columns = st.columns(len(recommended_stocks))
        
        for i, ticker in enumerate(recommended_stocks):
            stock_df = fy[fy['ticker']==ticker]
            
            current_price = list(stock_df['Close'])[0]
            probability = round(100 * (list(stock_df['probability'])[0]), 2)
            if fy_buys == False:
                delta_color = "off"
                if ticker in stocks_in_my_portfolio:
                    delta_msg = "Sell Shares"
                else:
                    delta_msg = "Short Stock"
                    
            else:
                delta_color = "normal"
                delta_msg = f"{probability}% Match"
            
            columns[i].metric(
                label=f"{ticker}",
                value=f"${current_price:,.2f}",
                delta=f"{delta_msg}",
                delta_color = delta_color
            )
    # return recommended_stocks

def generate_ymal_section(
    user_risk_level=USER_RISK_LEVEL
):
    """
    """
    st.markdown("## You Might Also Like")
    st.markdown('---')
    
    change_risk_level = st.toggle('Change My Risk Level', key='ChangeRiskLevel_on_Home')
    if change_risk_level:
        risk_level = st.slider(
            'Select your risk level:',
            min_value=1,
            max_value=10,
            value=1,
            step=1
        )
        recommendation_dict = ymal_recommendation_dict
    else:
        risk_level = user_risk_level
        recommendation_dict = dmh__i.calculate_ymal_recommended_stocks(risk_level)
        
    risk_msg = recommendation_dict['risk_msg']
    recommended_stocks = recommendation_dict['recommended_stocks']
    gains_df = recommendation_dict['recent_gain']
    
    st.write(f"{risk_msg}")
    
    ymal_placeholder = st.empty()
    with ymal_placeholder.container():
        columns = st.columns(len(recommended_stocks))
        
        for i, ticker in enumerate(recommended_stocks):
            stock_df = gains_df[gains_df['ticker']==ticker]
            
            current_price = list(stock_df['Close'])[0]
            pct_change = list(stock_df['pct_change'])[0]
            
            columns[i].metric(
                label=f"{ticker}",
                value=f"${current_price:,.2f}",
                delta=f"{pct_change:,.2f}% DoD",
            )
