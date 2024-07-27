# ----- Imports -----
import streamlit as st
import requests
from bs4 import BeautifulSoup
import html

import tensorflow
from transformers import pipeline, TFAutoModelForSeq2SeqLM, AutoTokenizer

import re

import litellm
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler    
from langchain import PromptTemplate, LLMChain
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

import pandas as pd
import numpy as np

from datetime import datetime
from dateutil.relativedelta import relativedelta

import yfinance as yf

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

from scipy.spatial.distance import cdist

from data.configs import STOCK_TICKERS_DICT

# ----- LLMHelpers -----
class LLMHelpers():
    """
    """
    ignored_article_headlines = [
        "google news",
        "verfiy you are a human",
        "we've detected unusual activity from your computer network",
    ]
    llm = Ollama(
        model='mistral',
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()]),
        temperature=0.9
    )
    summarization_model_name = "t5-small"
    summarization_pipeline = pipeline(
        "summarization",
        model=TFAutoModelForSeq2SeqLM.from_pretrained(summarization_model_name, from_pt=True),
        tokenizer=AutoTokenizer.from_pretrained(summarization_model_name),
        framework='tf'
        
    )
    
    ama_prompt_template = PromptTemplate(
        input_variables=['history', 'input'],
        template="""
        ### Instruction:
        TradeSocial is a personalized stock trading app that combines investment insights with various
        social networking features. Users can use TradeSocial to discover, connect, and invest smarter
        with a community-driven approach to stock trading. 
        
        You are an investment expert and assistant for the TradeSocial platform
        and you are trying to help non-expert and potentially
        new investors learn more about the stock market and how to invest. Read the prompt
        below and continue the conversation with the most appropriate response.
        
        Try your best not not to use too much financial jargon if it is not needed.
        
        All responses MUST be related to the stock market, finance, or investing, and must
        be less than 200 words.
        
        If you identify that the user is speficially asking about what stocks they should trade,
        respond to the user telling them to use TradeSocial's Explore Page.
        
        ### Conversation history:
        {history}
        
        ### Prompt:
        {input}
        """
    )
    classify_ama_user_input_prompt_template = PromptTemplate(
        input_variables=['history', 'input'],
        template="""
        ### Task:
        You are to determine user intent and classify a user's prompt
        into one of the following categories.
        
        1. Identify the user's intent:
        - If the user is asking about what stocks specifically to trade:
            - Response: "Specific question"
        
        - If the user is asking you to give them suggestions on what companies to trade:
            - Response: "Specific question"
        
        - If the user wants to know what to buy or sell:
            - Response: "Specific question"
        
        - If the user asking about anything else:
            - Response: "General question"
        
        ### Instruction:
        Read the user prompt and the conversation history, and then complete the task above.
        Think through what exactly the user is asking before you provide your classification.
        In your response, it should only be one from the options provided above -- 
        either "Specific question" or "General question".
        
        ### Conversation history:
        {history}
        
        ### Prompt:
        {input}
        """
    )
    
    def __init__(self):
        """
        """
        pass
    
    def generate_ama_classification(
        self,
        input_message,
        conversation_memory
    ):
        """
        """
        conversation_chain = LLMChain(
            llm=self.llm,
            prompt=self.classify_ama_user_input_prompt_template,
            memory=conversation_memory,
            verbose=True
        )
        llm_response = conversation_chain(input_message)
        return llm_response
    
    def generate_ama_llm_response(
        self,
        input_message,
        conversation_memory
    ):
        """
        """
        conversation_chain = LLMChain(
            llm=self.llm,
            prompt=self.ama_prompt_template,
            memory=conversation_memory,
            verbose=True
        )
        llm_response = conversation_chain(input_message)
        return llm_response
        
        
    def extract_headline_from_soup(
        self,
        soup
    ):
        """
        """
        headline_selectors = [
            {'tag': 'meta', 'attr': {'property': 'og:title'}},
            {'tag': 'meta', 'attr': {'name': 'twitter:title'}},
            {'tag': 'h1', 'class': 'headline'},
            {'tag': 'h1', 'class': 'article-title'},
            {'tag': 'h1', 'class': 'post-title'},
            {'tag': 'h1'},
            {'tag': 'h2'},
        ]
        
        for selector in headline_selectors:
            if 'attr' in selector:
                meta_tag = soup.find(selector['tag'], attrs=selector['attr'])
                if meta_tag and 'content' in meta_tag.attrs:
                    headline = html.unescape(meta_tag['content']).strip()
                    if headline.lower() not in self.ignored_article_headlines:
                        return headline
            elif 'class' in selector:
                headline_tag = soup.find(selector['tag'], class_=selector['class'])
                if headline_tag:
                    headline = html.unescape(headline_tag.get_text()).strip()
                    if 10 < len(headline) < 200 and headline.lower() not in self.ignored_article_headlines:
                        return headline
            else:
                headline_tag = soup.find(selector['tag'])
                if headline_tag:
                    headline = html.unescape(headline_tag.get_text()).strip() 
                    if 10 < len(headline) < 200 and headline.lower() not in self.ignored_article_headlines:
                        return headline
                # if headline_tag and 10 < len(headline_tag.get_text()) < 200:
                #     return html.unescape(headline_tag.get_text()).strip() 
        return "No headline found"
        
    
    def get_recent_news(
        self,
        ticker,
        max_results=7
    ):
        """
        """
        ticker = ticker.upper()
        articles_df = pd.DataFrame(columns=['ticker', 'url', 'headline', 'body'])
        article_urls = []
        article_headlines = []
        article_bodies = []
        
        google_news_url = "https://news.google.com"
        initial_url = f"{google_news_url}/search?q={ticker}&hl=en-US&gl=US&ceid=US%3Aen"
        initial_response = requests.get(initial_url)
        initial_soup = BeautifulSoup(initial_response.content, 'html.parser')
        
        for item in initial_soup.find_all('article')[:max_results]:
            link_in_a_tag = item.find('a', class_='WwrzSb')['href']
            article_url = f"{google_news_url}{link_in_a_tag}"
            
            article_response = requests.get(article_url)
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            article_headline = self.extract_headline_from_soup(article_soup)
            
            if ("No headline found" not in article_headline) and ("We've detected unusual activity from your computer network" not in article_headline):
                article_urls = article_urls + [article_url]
                article_headlines = article_headlines + [article_headline]
                
                paragraphs = article_soup.find_all('p')
                article_body = ' '.join([p.get_text() for p in paragraphs])
                article_bodies = article_bodies + [article_body]
        
        articles_df['ticker'] = [ticker] * len(article_urls)
        articles_df['url'] = article_urls
        articles_df['headline'] = article_headlines
        articles_df['body'] = article_bodies
        return articles_df
    
    def summarize_articles(
        self,
        articles
    ):
        """
        """
        summary_list = self.summarization_pipeline(
            articles,
            min_length=10,
            max_length=150,
            do_sample=False
        )
        summary_text = summary_list[0]['summary_text']
        summary_cleaned = ' '.join(summary_text.split())
        
        summary_sentence_case = re.sub(
            r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s",
            lambda m: m.group(0).capitalize(),
            summary_cleaned
        )
        return summary_sentence_case
