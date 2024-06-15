# ----- Imports -----
import streamlit as st

# ----- TradeSocial Profile Page -----
def generate_profile_page():
    """
    """
    st.markdown('# Profile')
    
    user_name = st.text_input('Username', 'notsoroaringkitty')
    user_email = st.text_input('Email', 'notsoroaringkitty@email.net')
    user_bio = st.text_area('Bio', 'DIAMOND HANDS TO THE MOON! 💎🤲🏾')
    
    st.markdown('---')
    
    st.markdown(f"**Username:** `{user_name}`")
    st.markdown(f"**Email:** `{user_email}`")
    st.markdown(f"**Bio:** `{user_bio}`")
    
    st.markdown('---')
    
    if st.button('Save changes', key='update_profile_on_profile_page'):
        st.success('Profile updated successfully!')
    