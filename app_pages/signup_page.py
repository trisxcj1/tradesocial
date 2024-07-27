# ----- Imports -----
import streamlit as st
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader
import os
from dotenv import load_dotenv

load_dotenv()
users_config_path = os.getenv('USERS_CONFIG_LOCATION')


with open(users_config_path) as file:
    users_config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    users_config['credentials'],
    users_config['cookie']['name'],
    users_config['cookie']['key'],
    users_config['cookie']['expiry_days'],
    users_config['pre-authorized']
)

def gen_signup_page(authenticator=authenticator):
    """
    """
    try:
        registration_user_email, registration_username, registration_name = authenticator.register_user(pre_authorization=False)
        # with open(users_config_path, 'w') as file:
        #     yaml.dump(users_config, file, default_flow_style=False)
        #     st.write(users_config)
        st.write(registration_user_email, registration_username, registration_name)
        return True
    except Exception as e:
        st.error(e)
        return False