# ----- Imports -----
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

import streamlit as st

import plotly.graph_objs as go
import plotly.express as px

from helpers.data_manipulation_helpers import DataManipulationHelpers
from data.configs import STOCK_TICKERS_DICT

dmh__i = DataManipulationHelpers()

# ----- TradeSocial Home Page Components -----

# TODO: improve
portfolio = {
    'AAPL': [{'quantity': 5, 'transaction_date': '2024-01-03'}, {'quantity': 7, 'transaction_date': '2024-02-02'}],
    'GOOGL': [{'quantity': 5, 'transaction_date': '2022-06-15'}],
    'MSFT': [{'quantity': 8, 'transaction_date': '2022-06-16'}]
}

# TODO: move to data manipulation helpers
def calculate_my_portfolio_metrics(portfolio=portfolio):
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
    
    # line_color = 'green' if pct_gain >=0 else 'red'
    gain_sign = '+' if portfolio_pct_change >=0 else '-'

    st.markdown(f"### Current Portfolio Value: ${current_portfolio_value:,.2f} ({gain_sign}{portfolio_pct_change}%)")    
    fig = px.pie(
        values=portfolio_value_df['current_value'],
        names=portfolio_value_df['ticker'],
        title=f"Breakdown of Current Portfolio Value"
    )
    st.plotly_chart(fig, use_container_width=True)

def generate_update_my_portfolio_section():
    st.markdown("### Update My Portfolio")
    
    with st.form(key='update_portfolio_form_on_home'):
        available_tickers = list(STOCK_TICKERS_DICT.keys())
        ticker = st.selectbox('Ticker', available_tickers)
        quantity = st.number_input('Quantity', min_value=1)
        transaction_date = st.date_input('Transaction Date', min_value=datetime(2000, 1, 1))
        transaction_type = st.selectbox('Transaction Type', ['Buy', 'Sell'])
        # submit_button = st.form_submit_button(label='Update Portfolio', key='update_portfolio_button_on_home')
        submit_button = st.form_submit_button(label='Update Portfolio')
        
        if submit_button:
            if transaction_type == 'Sell':
                quantity = -quantity
            if ticker in portfolio:
                portfolio[ticker].append({'quantity': quantity, 'transaction_date': transaction_date.strftime('%Y-%m-%d')})
            else:
                portfolio[ticker] = [{'quantity': quantity, 'transaction_date': transaction_date.strftime('%Y-%m-%d')}]

def generate_for_you_section():
    """
    """
    st.markdown("## For You")
    st.markdown('---')
    
    risk_level = st.slider(
        'Select your risk level:',
        min_value=1,
        max_value=10,
        value=1,
        step=1
    )
    recommendation_dict = dmh__i.calculate_recommended_stocks(risk_level)
    recommended_stocks = recommendation_dict['recommended_stocks']
    gains_df = recommendation_dict['recent_gain']
    
    placeholder = st.empty()
    with placeholder.container():
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
                