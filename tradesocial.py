# ----- Imports -----
import streamlit as st
st.set_page_config(page_title='TradeSocial 💸')

import streamlit_authenticator as stauth

import time 

import yaml
from yaml.loader import SafeLoader
import os
from dotenv import load_dotenv

from app_pages.welcome_page import WelcomePage
from app_pages.explore_page import generate_explore_page
from app_pages.profile_page import generate_profile_page
from app_pages.ask_me_anything_page import generate_ask_me_anything_page

load_dotenv()
users_config_path = os.getenv('USERS_CONFIG_LOCATION')
current_user_config_path = os.getenv('CURRENT_USERS_CONFIG_LOCATION')

# ----- TradeSocial -----
wp__i = WelcomePage()
show_onboarding_page = False

with open(users_config_path) as file:
    users_config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    users_config['credentials'],
    users_config['cookie']['name'],
    users_config['cookie']['key'],
    users_config['cookie']['expiry_days'],
    users_config['pre-authorized']
)

login_page_output = wp__i.gen_login_page()
name, authentication_status, username = login_page_output['auth']
hide_sign_up = True if authentication_status else False
signup_page_output = wp__i.gen_signup_page(hide=hide_sign_up)

if 'USER_USERNAME' not in st.session_state:
    st.session_state['USER_USERNAME'] = None
if 'USER_PORTFOLIO' not in st.session_state:
    st.session_state['USER_PORTFOLIO'] = {}
if 'USER_PORTFOLIO_GOAL' not in st.session_state:
    st.session_state['USER_PORTFOLIO_GOAL'] = 5000
if 'USER_PORTFOLIO_GOAL_DATE' not in st.session_state:
    st.session_state['USER_PORTFOLIO_GOAL_DATE'] = "2024-12-25"
if 'USER_RISK_LEVEL' not in st.session_state:
    st.session_state['USER_RISK_LEVEL'] = 1

if st.session_state['authentication_status']==True:
    user_info = users_config['credentials']['usernames'][username]
    portfolio_goal_date = user_info['portfolio_goal_date']
    
    st.session_state['USER_USERNAME'] = username
    st.session_state['USER_PORTFOLIO'] = user_info['portfolio']
    st.session_state['USER_PORTFOLIO_GOAL'] = user_info['portfolio_goal']
    st.session_state['USER_PORTFOLIO_GOAL_DATE'] = portfolio_goal_date
    st.session_state['USER_RISK_LEVEL'] = user_info['risk_level']

if st.session_state['USER_USERNAME'] is None:
    time.sleep(25)
    st.warning("Having trouble?")
    time.sleep(5)
    st.warning("Try refreshing the app")
    
from app_pages.home_page import generate_home_page

# creating a menu for users to tab between pages
tradesocial_pages_mapping = {
    'Home 🏡': generate_home_page,
    'Explore 🔎': generate_explore_page,
    'Ask Me Anything ✨': generate_ask_me_anything_page,
}
tradesocial_pages_menu_items = list(tradesocial_pages_mapping.keys())

if st.session_state['authentication_status']==True:
    with st.sidebar:
        st.markdown("# TradeSocial 💸")
        st.markdown(
            f"""
            **TradeSocial** is a personalized stock trading application
            that combines investment insights with social networking features.
            
            Discover, connect, and invest smarter with a community-driven approach
            to stock trading.
            """
        )
        st.markdown('---')
        st.sidebar.write(f'Hi, **{name}**')
        selected_page = st.selectbox('Menu', tradesocial_pages_menu_items)
        
        if selected_page == "Ask Me Anything ✨":
            st.markdown(
                """
                <p style="font-size:12px;">
                TradeSocial Assistant is here to help but can make mistakes.
                Please verify important information.
                </p>
                """,
                unsafe_allow_html=True
            )
        
        authenticator.logout()

    # displaying the selected page
    tradesocial_pages_mapping[selected_page]()
    
elif st.session_state['authentication_status'] is False:
    st.error('Sorry, incorrect username or password 😕')
