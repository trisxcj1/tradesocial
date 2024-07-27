# ----- Imports -----
import streamlit as st
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader
import os
from dotenv import load_dotenv

import time

from helpers.data_manipulation_helpers import DataManipulationHelpers
from data.configs import (
    STOCK_TICKERS_DICT
)


load_dotenv()
users_config_path = os.getenv('USERS_CONFIG_LOCATION')

# ----- Welcome -----
with open(users_config_path) as file:
    users_config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    users_config['credentials'],
    users_config['cookie']['name'],
    users_config['cookie']['key'],
    users_config['cookie']['expiry_days'],
    users_config['pre-authorized']
)

class WelcomePage:
    def __init__(self):
        """
        """
        pass

    def gen_signup_page(self, authenticator=authenticator, hide=False):
        """
        """
        new_user = False
        if hide:
            return False
        else:
            st.markdown("### OR")
            
            try:
                registration_user_email, registration_username, registration_name = authenticator.register_user(
                    pre_authorization=False,
                    fields={
                        'Form name': 'Sign Up For TradeSocial 💸',
                        'Email':'Email Address',
                        'Username':'Username',
                        'Password':'Password 🙈',
                        'Repeat password':'Password Again, sorry...',
                        'Register':"Let's Go! 🚀"
                    }
                )
                if registration_user_email:
                    users_config['credentials']['usernames'][registration_username]['portfolio'] = {}
                    users_config['credentials']['usernames'][registration_username]['risk_level'] = 1
                    with open(users_config_path, 'w') as file:
                        yaml.dump(users_config, file, default_flow_style=False)
                    st.success('You have successfully registered! Now go back to Login to get started.')
                    
            except Exception as e:
                st.error(e)
                
    
    def gen_login_page(self, authenticator=authenticator):
        """
        """
        # if show_intro:
        #     st.markdown("# TradeSocial 💸")
        #     st.markdown(
        #         f"""
        #         **TradeSocial** is a personalized stock trading application
        #         that combines investment insights with social networking features.
                
        #         Discover, connect, and invest smarter with a community-driven approach
        #         to stock trading.
        #         """
        #     )
        #     st.markdown("---")
        auth_output = authenticator.login(
            fields={
                'Form name': 'Log into TradeSocial 💸',
                'Username':'Username',
                'Password':'Password 🙈',
                'Login':'Login 😎'
            }
        )
        output = {'auth': auth_output}
        return output
    
    def gen_onboarding_questionnaire(self):
        """
        """
        st.markdown("# Help us learn more about you")
        st.markdown("---")
        
        portfolio = {}
        
        st.markdown(
            f"""
            ## First, let's start with your trading history.
            """
        )
        previous_trades = st.radio(
            "Do you have any previous trades you would like to log?",
            ("Yes, I have previous trades", "No, I don't have any trades yet"),
            index=None
        )
        if previous_trades=="No, I don't have any trades yet":
            st.markdown(
                f"""
                It's the perfect time to get started! Be sure to check out the Explore Page.
                """
            )
            
        elif previous_trades=="Yes, I have previous trades":
            st.markdown("Amazing! Let's let you get those traded logged.")
            
            with st.form(key='LogTrades_on_Onboarding'):
                available_tickers = list(STOCK_TICKERS_DICT.keys())
                ticker = st.selectbox('Ticker', available_tickers)
                quantity = st.number_input('Quantity', min_value=1)
                transaction_date = st.date_input('Transaction Date', min_value=datetime(2000, 1, 1))
                transaction_type = st.selectbox('Transaction Type', ['Buy'])
                submit_button = st.form_submit_button(label='Update Portfolio')
                
                if submit_button:
                    if ticker in portfolio:
                        portfolio[ticker].append({'quantity': quantity, 'transaction_date': transaction_date.strftime('%Y-%m-%d')})
                    else:
                        portfolio[ticker] = [{'quantity': quantity, 'transaction_date': transaction_date.strftime('%Y-%m-%d')}]
                    st.write(f"{ticker} {transaction_date} transaction logged.")
        
        risk_level = st.slider(
            "Set your risk level",
            min_value=1,
            max_value=10,
            step=1
        )
        
