# ----- Imports -----
import streamlit as st

from app_pages.home_page import generate_home_page
from app_pages.explore_page import generate_explore_page
from app_pages.profile_page import generate_profile_page
from app_pages.unknown_page import generate_unknown_page

# ----- TradeSocial -----
st.set_page_config(page_title='TradeSocial 💸')


# creating a manu for users to tab between pages
tradesocial_pages_mapping = {
    'Explore': generate_explore_page,
    'Home': generate_home_page,
    'Explore': generate_explore_page,
    'Community': generate_unknown_page,
    'Profile': generate_profile_page
}
tradesocial_pages_menu_items = list(tradesocial_pages_mapping.keys())

# displaying the selected page
with st.sidebar:
    st.markdown("# TradeSocial 💸")
    st.markdown('---')
    selected_page = st.selectbox('Menu', tradesocial_pages_menu_items)
    
tradesocial_pages_mapping[selected_page]()