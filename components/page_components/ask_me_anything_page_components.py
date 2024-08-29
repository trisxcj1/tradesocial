# ----- Imports -----
import streamlit as st
import random

from langchain.memory import ConversationBufferMemory

from helpers.llm_helpers import LLMHelpers

llmh__i = LLMHelpers()

conversation_memory = ConversationBufferMemory()

# ----- TradeSocial Ask Me Anything Page Components -----
def generate_ama_chat_bot():
    """
    """
    first_msg = 'Hello! How can I help you today?'
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    else:
        for message in st.session_state.chat_history:
            conversation_memory.save_context(
                {'input': message['human']},
                {'output': message['AI']}
            )
    
    if 'messages' not in st.session_state:
        st.session_state['messages'] = [{
            'role': 'assistant',
            'content': first_msg
        }]
        st.markdown(f"## {first_msg}")

    for message in st.session_state.messages[1:]:
        st.chat_message(message['role']).write(message['content'])
    
    if user_input_message := st.chat_input(key='general-user-input'):
        st.session_state.messages.append({'role': 'user', 'content': user_input_message})
        st.chat_message('user').write(user_input_message)
        
        # ama_classification = llmh__i.generate_ama_classification(user_input_message, conversation_memory)['text']
        # if 'general question' in ama_classification.lower():
        #     llm_reply = llmh__i.generate_ama_llm_response(user_input_message, conversation_memory)
        # else:
        #     llm_reply = {
        #         'text': """
        #         Although I cannot tell you exactly what to do, TradeSocial's Explore Page
        #         provides a variety of tools for you to identify trends and uncover trades
        #         that can help maximize your portfolio!
        #         """
        #     }
        llm_reply = llmh__i.generate_ama_llm_response(user_input_message, conversation_memory)
        
        st.session_state.messages.append({'role': 'assistant', 'content': llm_reply['text']})
        st.chat_message('assistant').write(llm_reply['text'])
        message = {'human': user_input_message, 'AI': llm_reply['text']}
        st.session_state.chat_history.append(message)
