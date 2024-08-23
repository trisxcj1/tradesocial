# ----- Imports -----
import math 
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
    USER_RISK_LEVEL,
    USER_PORTFOLIO_GOAL,
    USER_PORTFOLIO_GOAL_DATE
)

dmh__i = DataManipulationHelpers()

load_dotenv()
users_config_path = os.getenv('USERS_CONFIG_LOCATION')
current_user_config_path = os.getenv('CURRENT_USERS_CONFIG_LOCATION')

# ----- TradeSocial Home Page Components -----
portfolio = USER_PORTFOLIO
fy_recommendations = dmh__i.claculate_fy_recommended_stocks(USER_RISK_LEVEL)['recommended_stocks'] # risk level is not currently being used
fy_quick_recommendations = dmh__i.claculate_fy_recommended_stocks(USER_RISK_LEVEL, quick_fy=True)['recommended_stocks'] # risk level is not currently being used
ymal_recommendation_dict = dmh__i.calculate_ymal_recommended_stocks(USER_RISK_LEVEL)

personalization_evolution_note = """
This feature is powered by AI algorithms and adapts to your preferences and behavior.
The more you use it, the more tailored and accurate it becomes for you. Your feedback
and interactions help use continuously enhance its performance.
"""

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

def update_my_goal(
    suggested_goal,
    suggested_date
):
    """
    """
    update_my_goal = st.toggle('Update My Goal', key='UpdateMyGoalToggle_on_Home')
    
    if update_my_goal:
        with st.form(key='UpdateMyGoalForm_on_Home'):
            new_goal_amount = st.number_input('New Goal Amount', value=suggested_goal)
            new_goal_date = st.date_input('New Target Date', value=suggested_date, min_value=datetime.today())
            
            submit_button = st.form_submit_button(label='Save New Goal')
            
            if submit_button:
                with open(current_user_config_path, 'w') as current_user_py_file:
                    current_user_py_file.write(f"USER_USERNAME = '{USER_USERNAME}'\n")
                    current_user_py_file.write(f"USER_PORTFOLIO = {USER_PORTFOLIO}\n")
                    current_user_py_file.write(f"USER_PORTFOLIO_GOAL = {new_goal_amount}\n")
                    current_user_py_file.write(f"USER_PORTFOLIO_GOAL_DATE = '{new_goal_date}'\n")
                    current_user_py_file.write(f"USER_RISK_LEVEL = {USER_RISK_LEVEL}")
                
                with open(current_user_config_path) as file:
                    users_config = yaml.load(file, Loader=SafeLoader)
                    
                users_config['credentials']['usernames'][USER_USERNAME]['portfolio_goal'] = new_goal_amount
                users_config['credentials']['usernames'][USER_USERNAME]['portfolio_goal_date'] = new_goal_date
                with open(current_user_config_path, 'w') as file:
                    yaml.dump(users_config, file, default_flow_style=False)
                
                st.success("Goal Updated 👍🏽")
        

def gen_track_my_portfolio_goal_section(
    portfolio=portfolio,
    risk_level=USER_RISK_LEVEL,
    goal=USER_PORTFOLIO_GOAL,
    goal_date=USER_PORTFOLIO_GOAL_DATE
):
    """
    """
    risk_level_mappings = {
        1: 0.02, 2: 0.08, 3: 0.16, 4: 0.22, 5: 0.30,
        6: 0.35, 7: 0.45, 8: 0.60, 9: 0.72, 10: 0.80,
        11: 0.97
    }
    risk_level = 10 if risk_level >= 10 else risk_level
    
    portfolio_over_time = calculate_my_portfolio_metrics_over_time()
    
    today = datetime.today()
    goal_date = datetime.strptime(goal_date, "%Y-%m-%d")
    
    time_remaining_until_goal_date = (goal_date - today).days
    
    if len(portfolio_over_time) > 0:
        
        portfolio_value_df = calculate_my_portfolio_metrics()
        portfolio_value_df = (
            portfolio_value_df[portfolio_value_df['current_value']>0]    
        )
        current_portfolio_value = (
            portfolio_value_df
            ['current_value']
            .sum()
        )
        
        pct_increase_needed = 100 * (goal - current_portfolio_value) / current_portfolio_value
        daily_pct_increase_needed = pct_increase_needed / time_remaining_until_goal_date
        risk_level_daily_pct = risk_level_mappings[risk_level]
        next_risk_level_daily_pct = risk_level_mappings[risk_level+1]
        
        estimated_days_required = math.log(goal / current_portfolio_value) / math.log(1 + (risk_level_daily_pct/100))
        estimated_days_difference = estimated_days_required - time_remaining_until_goal_date
        new_goal_date = goal_date + relativedelta(days=estimated_days_difference + 30)
        push_goal_date = today + relativedelta(days=252)

        new_goal = round(current_portfolio_value * ((1 + (risk_level_daily_pct/100)) ** time_remaining_until_goal_date), 0)
        if new_goal >= goal:
            outstanding_difference = goal - current_portfolio_value
            new_goal = round(current_portfolio_value + (outstanding_difference * 0.97), 0)
        push_goal = round(current_portfolio_value * ((1 + (next_risk_level_daily_pct/100)) ** 252), 0)
        
        st.markdown("## My Portfolio Goal")
        st.markdown("---")
        
        
        portfolio_progress = current_portfolio_value/goal
        portfolio_progress = 1.0 if portfolio_progress >= 1 else portfolio_progress
        portfolio_progress_pct = round(100 * portfolio_progress, 0)
        portfolio_progress_pct = int(portfolio_progress_pct)
        
        st.markdown(f"### You are currently {portfolio_progress_pct}% of the way towards your ${goal:,} portfolio goal")
        st.progress(portfolio_progress)
        
        if (time_remaining_until_goal_date > 1) and (portfolio_progress < 0.95):
            if daily_pct_increase_needed > risk_level_daily_pct:
                st.markdown(
                    f"""
                    Your goal is to be at ${goal:,} by {goal_date.strftime("%B %d, %Y")}.
                    """
                )
                st.markdown(
                    f"""
                    You are currently at ${current_portfolio_value:,.2f} with {time_remaining_until_goal_date} days
                    remaining until your goal date.
                    """
                )
                st.markdown(
                    f"""
                    Given your risk level, you might be uncomfortable making the types of trades necessary to still hit your goal
                    within your timeframe. Therefore, we suggest either:
                    - Extending your goal to be ${goal:,} by {new_goal_date.strftime("%B %d, %Y")} `Recommended`
                    - Updating your goal to be ${new_goal:,} by {goal_date.strftime("%B %d, %Y")}
                    """
                )
                update_my_goal(goal, new_goal_date)
                
            else:
                st.markdown(
                    f"""
                    Your goal is to be at ${goal:,} by {goal_date.strftime("%B %d, %Y")}.
                    """
                )
                st.markdown(
                    f"""
                    Your are currently at ${current_portfolio_value:,.2f}, and you are on track to achieve your goal since
                    you have {time_remaining_until_goal_date} days remaining until your deadline.
                    
                    Remember that the stock market is volatile and things can change quickly. Be sure to keep an eye on your
                    portfolio's value as well as your recommended trades to give you the best chance at success.
                    """
                )
                update_my_goal(push_goal, push_goal_date)
        
        if (time_remaining_until_goal_date > 1) and (portfolio_progress >= 0.95):
            st.markdown(
                f"""
                You're a rockstar!
                
                Although you have more time remaining to achieve your goal, you're already so close that we think
                it's time to push you towards a new goal 🔥
                
                We think you can aim for ${push_goal:,} by {push_goal_date.strftime("%B %d, %Y")}
                """
            )
            update_my_goal(push_goal, push_goal_date)
        
        if (time_remaining_until_goal_date == 1) and (portfolio_progress < 0.95):
            st.markdown(
                f"""
                You gave it a good fight, but time was not on our side. Let's keep on pushing and try with a new goal 💪
                
                What do think about ${push_goal:,} by {push_goal_date.strftime("%B %d, %Y")}?
                """
            )
            update_my_goal(push_goal, push_goal_date)
        
        if (time_remaining_until_goal_date == 1) and (portfolio_progress >= 0.95):
            st.markdown(
                f"""
                You have 1 day left, but why wait?
                
                We think you're ready for a new challenge! Let's try ${push_goal:,} by {push_goal_date.strftime("%B %d, %Y")} 😎
                """
            )
            update_my_goal(push_goal, push_goal_date)
            
        if (time_remaining_until_goal_date < 1) and (portfolio_progress < 0.95):
            st.markdown(
                f"""
                It looks like time slipped away from us. The good news is, it's never too late to start a new goal 😉.
                
                ${push_goal:,} by {push_goal_date.strftime("%B %d, %Y")}? Let's get started today.
                """
            )
            update_my_goal(push_goal, push_goal_date)
            
        if (time_remaining_until_goal_date < 1) and (portfolio_progress >= 0.95):
            st.markdown(
                f"""
                So close 🥲.
                
                Let's aim for ${push_goal:,} by {push_goal_date.strftime("%B %d, %Y")} -- I know you can get this one.
                """
            )
            update_my_goal(push_goal, push_goal_date)
        
        
    else:
        st.warning("Start adding to your portfolio to get closer to your goal!")
    

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
        
        portfolio_agg_level = st.toggle('Show Portfolio Distribution', key='ShowPortfolioDistributionToggle_on_Home')
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
    with st.form(key=f'UpdateMyPortfolioFrom_on_Home_{portfolo_update_counter}'):
        available_tickers = list(STOCK_TICKERS_DICT.keys())
        ticker = st.selectbox('Ticker', available_tickers)
        quantity = st.number_input('Quantity', min_value=1)
        transaction_date = st.date_input('Transaction Date', min_value=datetime(2000, 1, 1))
        transaction_type = st.selectbox('Transaction Type', ['Buy', 'Sell'])
        submit_button = st.form_submit_button(label='Update Portfolio')
        
        # # NOTE: turning this off for now because it REALLY NEEDS to be batch processing
        # investors_also_bought = dmh__i.gen_investors_also_bought(
        #     stock_association_rules,
        #     ticker
        # )
        
        if submit_button:
            portfolo_update_counter += 1
            if transaction_type == 'Sell':
                quantity = -quantity
                st.success(f"Sold {STOCK_TICKERS_DICT[ticker]} ({ticker})!")
            else:
                st.success(f"Purchased {STOCK_TICKERS_DICT[ticker]} ({ticker})!")
                
                # # NOTE: turning this off for now because it REALLY NEEDS to be batch processing
                # if investors_also_bought is not None:
                #     consequent = investors_also_bought.iloc[0]['consequents']
                #     consequent_str = ' + '.join(list(consequent))
                #     st.write(f"TradeSocial investors who purchased `{ticker}` also purchased ```{consequent_str}```")
                    
            st.error(
                f"""
                Sometimes if you try to log multiple transactions or when you leave the
                Update My Portfolio screen, TradeSocial crashes 😕
                
                It's not you, it's us. We are sorry for this inconvenience as this is not
                the intended experience. If this does happen to you, refreshing the app
                usually solves the problem.
                
                Please  bear with us as we work to fix this issue.
                """
            )
            st.markdown("<script>location.reload(true);</script>", unsafe_allow_html=True)
                
            if ticker in portfolio:
                portfolio[ticker].append({'quantity': quantity, 'transaction_date': transaction_date.strftime('%Y-%m-%d')})
            else:
                portfolio[ticker] = [{'quantity': quantity, 'transaction_date': transaction_date.strftime('%Y-%m-%d')}]
            
            with open(current_user_config_path, 'w') as current_user_py_file:
                current_user_py_file.write(f"USER_USERNAME = '{USER_USERNAME}'\n")
                current_user_py_file.write(f"USER_PORTFOLIO = {portfolio}\n")
                current_user_py_file.write(f"USER_PORTFOLIO_GOAL = {USER_PORTFOLIO_GOAL}\n")
                current_user_py_file.write(f"USER_PORTFOLIO_GOAL_DATE = '{USER_PORTFOLIO_GOAL_DATE}'\n")
                current_user_py_file.write(f"USER_RISK_LEVEL = {USER_RISK_LEVEL}")
            
            
            with open(users_config_path) as file:
                users_config = yaml.load(file, Loader=SafeLoader)
            users_config['credentials']['usernames'][USER_USERNAME]['portfolio'] = portfolio
            
            with open(users_config_path, 'w') as file:
                yaml.dump(users_config, file, default_flow_style=False)
            
            

def generate_quick_wins_section(
    portfolio=portfolio,
    buys=True
):
    """
    """
    portfolio_over_time = calculate_my_portfolio_metrics_over_time()
    if len(portfolio_over_time) > 0:
        stocks_in_my_portfolio = list(portfolio.keys())
        fy = fy_quick_recommendations['buys']
        stocks_in_ymal = ymal_recommendation_dict['recommended_stocks']
        stocks_in_fy_buys = fy_recommendations['buys']['ticker'][:8]
        stocks_in_fy_sells = fy_recommendations['sells']['ticker'][:8]
        
        st.markdown(f"## Your 7-Day Growth Opportunities ✨")
        st.markdown(f"<p style='font-size:12px;'>{personalization_evolution_note}</p>", unsafe_allow_html=True)
        st.markdown('---')
        st.markdown(
            f"""
            Here are a few quick wins we think you'll love. 
            
            Based on today's market conditions, these stocks are predicted
            to increase in value within the next 7 days. Keep an eye on
            these recommendations to potentially capitalize on short-term
            opportunities.
            """
        )
        recommended_stocks = list(
            fy[
                (~fy['ticker'].isin(stocks_in_ymal)) &
                (~fy['ticker'].isin(stocks_in_fy_buys)) &
                (~fy['ticker'].isin(stocks_in_fy_sells)) &
                (~fy['ticker'].isin(stocks_in_my_portfolio))
            ]
            .head(8)
            ['ticker']
        )
        
        quick_wins_placeholder_1 = st.empty()
        quick_wins_placeholder_2 = st.empty()
        
        with quick_wins_placeholder_1.container():
            columns_1 = st.columns(4)
            for i, ticker in enumerate(recommended_stocks[:4]):
                stock_df = fy[fy['ticker']==ticker]
                current_price = list(stock_df['Close'])[0]
                probability = round(100 * (list(stock_df['probability'])[0]), 2)
                delta_msg = f"{probability}% Match"
                columns_1[i].metric(
                    label=f"{ticker}",
                    value=f"${current_price:,.2f}",
                    delta=f"{delta_msg}"
                )
        
        with quick_wins_placeholder_2.container():
            columns_2 = st.columns(len(recommended_stocks) - 4)
            for i, ticker in enumerate(recommended_stocks[4:]):
                stock_df = fy[fy['ticker']==ticker]
                current_price = list(stock_df['Close'])[0]
                probability = round(100 * (list(stock_df['probability'])[0]), 2)
                delta_msg = f"{probability}% Match"
                columns_2[i].metric(
                    label=f"{ticker}",
                    value=f"${current_price:,.2f}",
                    delta=f"{delta_msg}"
                )
        
    else:
        st.warning("Add to your portfolio to see more of your recommendations")
        
    
def generate_fy_section(
    portfolio=portfolio,
    fy_buys=True
    # should also be based on risk level or something
):
    """
    """
    portfolio_over_time = calculate_my_portfolio_metrics_over_time()
    if len(portfolio_over_time) > 0:
    
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
        st.markdown(f"<p style='font-size:12px;'>{personalization_evolution_note}</p>", unsafe_allow_html=True)
        st.markdown('---')
        
        st.write(fy_msg)
        
        # deduplicating for stocks that will be in YMAL
        stocks_in_ymal = ymal_recommendation_dict['recommended_stocks']
        recommended_stocks = list(
            fy[~fy['ticker'].isin(stocks_in_ymal)]
            .head(8)
            ['ticker']
        )
        fy_placeholder_1 = st.empty()
        fy_placeholder_2 = st.empty()
        
        # showing 2 rows if more than 4 recommended stocks
        if len(recommended_stocks) > 4:
            
            # row 1 of recomemndations
            with fy_placeholder_1.container():
                columns_1 = st.columns(4)
                for i, ticker in enumerate(recommended_stocks[:4]):
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
                    
                    columns_1[i].metric(
                        label=f"{ticker}",
                        value=f"${current_price:,.2f}",
                        delta=f"{delta_msg}",
                        delta_color = delta_color
                    )
            # row 2 of recommendations        
            with fy_placeholder_2.container():
                columns_2 = st.columns(len(recommended_stocks) - 4)
                for i, ticker in enumerate(recommended_stocks[4:]):
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
                    
                    columns_2[i].metric(
                        label=f"{ticker}",
                        value=f"${current_price:,.2f}",
                        delta=f"{delta_msg}",
                        delta_color = delta_color
                    )    
        # only showing 1 more since its less that 4 recommendations            
        else:            
            with fy_placeholder_1.container():
                columns = st.columns(len(recommended_stocks))
                for i, ticker in enumerate(recommended_stocks[:5]):
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
        
    else:
        st.warning("Add to your portfolio to see more of your recommendations")

def generate_ymal_section(
    portfolio=portfolio,
    user_risk_level=USER_RISK_LEVEL
):
    """
    """
    portfolio_over_time = calculate_my_portfolio_metrics_over_time()
    if len(portfolio_over_time) > 0:
        st.markdown("## You Might Also Like")
    else:
        st.markdown("## We Think You'll Be Interested In")
    st.markdown('---')
    
    change_risk_level = st.toggle('Change My Risk Level', key='ChangeRiskLevelToggle_on_Home')
    if change_risk_level:
        risk_level = st.slider(
            'Select your risk level:',
            min_value=1,
            max_value=10,
            value=USER_RISK_LEVEL,
            step=1
        )
        st.markdown(f"Your risk level is currently `Level {USER_RISK_LEVEL}`")
        st.markdown(
            """
            Read the following descriptions and choose the risk level that you believe best suits you:
            
            **Risk Level 1 (Very Conservative)**: You want to participate in the stock market while
            with as minimal risk as possible. You prefer the safest route with little to no ips and
            downs in your investment value. Your returns might be small but steady.
            
            **Risk Levels 2-3 (Conservative)**: You are seeking slightly higher returns while still
            prioritizing safety. You prefer to play it safe, but you are open to minor fluctuations
            that can increase your portfolio's value.
            
            **Risk Level 4 (Conservatiley Moderate)**: You are open to some risks for the potential of
            higher returns. You want to see some more growth in your investments while still keeping 
            things relatively stable.
            
            **Risk Level 5 (Moderate)**: You are willing to accept moderate fluctuations for potentially
            higher gains. You are comfortable with the ups and downs, and you undertsand that sometimes
            you might gain more and other times you might lose more.
            
            **Risk Levels 6-7 (Moderately Aggressive)**: You are comfortable with significant market exposure.
            You are looking for growth and you are not too worried about the possibility of more frequent
            fluctuations in your investment value.
            
            **Risk Level 8 (Aggressive)**: You are seeking substantial growth and you are willing to accept
            high volatility, knowing that you can win big if you strike the right trade. You are comfortable
            with significant and frequent changes in your investment value, including some losses.
            
            **Risk Level 9 (Very Aggressive)**: You want to prioritize maximum returns over stability and 
            you are comfortable with the possibility of substantial losses.
            
            **Risk Level 10 (Extremely High Risk)**: You want to risk it all. You know the the stock market
            can provide astronomical retruns, and that it can take it all away. You are willing to take part
            in high-stakes trading in volatile and speculative markets, with the clear understanding that
            they could either gain or lose significantly.
            """
        )
        recommendation_dict = dmh__i.calculate_ymal_recommended_stocks(risk_level)
    else:
        recommendation_dict = ymal_recommendation_dict
        
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
