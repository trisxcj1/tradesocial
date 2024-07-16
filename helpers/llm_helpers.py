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
    
    # article_summary_prompt_template = PromptTemplate(
    #     input_variables=['articles'],
    #     template="""
    #     ### Instruction:
    #     You are an investment expert who is tryig to help retail investors understand what
    #     is happening within the stock market. These retail investors are not industry experts
    #     and they are not expected to have a background in finance.
        
    #     You are the read the following articles and
    #     provide a very short summary about the articles.
        
    #     If there are multiple articles, do not provide a summary for each.
    #     Just provide a single short summary.
        
    #     This summary should be short! No more than 80 words.
        
    #     Remember, keep it short and to the point. Only provide a summary and do not elaborate on points.
        
    #     ### Articles:
    #     {articles}
    #     """
    # )
    article_summary_prompt_template = PromptTemplate(
        input_variables=['articles'],
        template="""
        ### Instruction:
        You are to read the following articles and provide a single, short,
        concise but informative summary about the articles in 30 words or less.
        
        If there are multiple articles, do not provide a summary for each.
        Just provide a single, short, concise but informative summary about the articles.
        
        This summary must be no more than 30 words.
        
        Remember, keep it short and to the point. Only provide a summary and do not elaborate on points.
        
        If the summary is longer than 30 words, you must rewrite it to fit within the word limit.
        
        Keep it short!
        
        ### Articles:
        {articles}
        """
    )
    
    def __init__(self):
        """
        """
        pass
    
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
                    return html.unescape(meta_tag['content']).strip()
            elif 'class' in selector:
                headline_tag = soup.find(selector['tag'], class_=selector['class'])
                if headline_tag and 10 < len(headline_tag.get_text()) < 200:
                    return html.unescape(headline_tag.get_text()).strip()
            else:
                headline_tag = soup.find(selector['tag'])
                if headline_tag and 10 < len(headline_tag.get_text()) < 200:
                    return html.unescape(headline_tag.get_text()).strip() 
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
            max_length=75,
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
        
