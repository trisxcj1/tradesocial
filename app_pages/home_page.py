# ----- Imports -----
import streamlit as st

from components.page_components.home_page_components import (
    generate_my_portfolio_section,
    generate_update_my_portfolio_section,
    generate_fy_section,
    generate_ymal_section
)


# ----- TradeSocial Home Page -----
def generate_home_page():
    """
    """
    st.markdown('# Home')
    st.markdown(
        """
        The idea of `TradeSocial` is to create a personalized stock trading app that
        combines investment insights with social networking features.
        Discover, connect, and invest smarter with a community-driven approach to stock trading.
        """
    )
    
    # My portfolio
    st.markdown('## My Portfolio')
    st.markdown('---')
    
    update_my_portfolio = st.toggle('Update My Portfolio', key='UpdateMyPortfolio_on_Home')
    if update_my_portfolio:
        generate_update_my_portfolio_section()

    generate_my_portfolio_section()
    
    # Buys For You
    generate_fy_section()
    
    # YMAL
    generate_ymal_section()
    
    # Recommended Sells
    generate_fy_section(False)
