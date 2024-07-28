# ----- Imports -----
import streamlit as st
st.set_page_config(page_title='TradeSocial 💸')

import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader
import os
from dotenv import load_dotenv

from app_pages.welcome_page import WelcomePage
from app_pages.home_page import generate_home_page
from app_pages.explore_page import generate_explore_page
from app_pages.profile_page import generate_profile_page
from app_pages.unknown_page import generate_unknown_page
from app_pages.ask_me_anything_page import generate_ask_me_anything_page

load_dotenv()
users_config_path = os.getenv('USERS_CONFIG_LOCATION')
current_user_config_path = os.getenv('CURRENT_USERS_CONFIG_LOCATION')


# ----- TradeSocial -----
wp__i = WelcomePage()
show_onboarding_page = False

# creating a menu for users to tab between pages
tradesocial_pages_mapping = {
    'Home 🏡': generate_home_page,
    'Explore 🔎': generate_explore_page,
    'Ask Me Anything ✨': generate_ask_me_anything_page,
    # 'Community 👥': generate_unknown_page,
    # 'Learn 📚': generate_unknown_page,
    # 'Profile 😎': generate_profile_page
}
tradesocial_pages_menu_items = list(tradesocial_pages_mapping.keys())

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

if st.session_state['authentication_status']==True:
    user_info = users_config['credentials']['usernames'][username]
    with open(current_user_config_path, 'w') as current_user_file:
        current_user_file.write(f"USER_USERNAME = '{username}'\n")
        current_user_file.write(f"USER_PORTFOLIO = {user_info['portfolio']}\n")
        current_user_file.write(f"USER_RISK_LEVEL = {user_info['risk_level']}")
        
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
        authenticator.logout()

    # displaying the selected page
    tradesocial_pages_mapping[selected_page]()
    
elif st.session_state['authentication_status'] is False:
    st.error('Sorry, incorrect username or password 😕')
