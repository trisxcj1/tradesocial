# ----- Imports -----
import pandas as pd

from datetime import datetime
from dateutil.relativedelta import relativedelta

import yfinance as yf

from data.configs import STOCK_TICKERS_DICT

# ----- DataManipulationHelpers -----
class DataManipulationHelpers():
    """
    """
    
    def __init__(self):
        """
        """
        pass
    
    def get_ystock_data_over_time(
        self,
        ticker,
        start_date=None,
        end_date='most recent trading day'
    ):
        """
        """
        today = datetime.today()
        
        if end_date in ['', 'yesterday', 'y']:
            end_date = today + relativedelta(days=-1)
            
        if end_date in ['most recent trading day']:
            end_date = today + relativedelta(days=-1)
            day_of_week = end_date.weekday()
            
            if day_of_week == 0:
                end_date = end_date + relativedelta(days=-3)
            elif day_of_week == 6:
                end_date = end_date + relativedelta(days=-2)
            elif day_of_week == 5:
                end_date = end_date + relativedelta(days=-1)
            
        if start_date in ['', None]:
            start_date = end_date + relativedelta(days=-30)
        
        if start_date in ['', 'yesterday', 'y']:
            start_date = today + relativedelta(days=-1)
            
        if start_date in ['most recent trading day']:
            start_date = today + relativedelta(days=-1)
            day_of_week = start_date.weekday()
            
            if day_of_week == 0:
                start_date = start_date + relativedelta(days=-3)
            elif day_of_week == 6:
                start_date = start_date + relativedelta(days=-2)
            elif day_of_week == 5:
                start_date = start_date + relativedelta(days=-1)
        
        if start_date == end_date:
            end_date = start_date + relativedelta(days=1)
            
        df = yf.download(ticker, start=start_date, end=end_date)
        df['ticker'] = [ticker] * len(df)
        return df
    
    def calculate_percentage_gain(
        self,
        df,
        scope='stock',
        interval='daily',
        value_col_name='Close'
    ):
        """
        """
        # TODO: calculate based on different intervals
        
        if scope == 'stock':
            gain_df = (
                df
                .sort_values(['ticker', 'Date'])
                .groupby('ticker')
                .tail(2)
            )
            
            gain_df['pct_change'] = (
                gain_df
                .groupby('ticker')
                [value_col_name]
                .pct_change() * 100
            )
            gain_df = gain_df.dropna(subset=['pct_change'])
        
        return gain_df
    
    def calculate_portfolio_value(
        self,
        portfolio_df
    ):
        """
        """
        flattened_portfolio = (
            portfolio_df
            .groupby('ticker')
            .agg(
                total_quantity = pd.NamedAgg('quantity', 'sum'),
                avg_initial_price = pd.NamedAgg('initial_price', 'mean'),
                current_price = pd.NamedAgg('current_price', 'mean')
            )
        )
        flattened_portfolio = flattened_portfolio.reset_index()
        flattened_portfolio['avg_initial_value'] = flattened_portfolio['total_quantity'] * flattened_portfolio['avg_initial_price']
        flattened_portfolio['current_value'] = flattened_portfolio['total_quantity'] * flattened_portfolio['current_price']
        
        return flattened_portfolio
    
    def calculate_recommended_stocks(
        self,
        risk_level
    ):
        """
        """
        # risk_level = risk_level/10
        all_stocks = list(STOCK_TICKERS_DICT.keys())
        
        stocks_df = pd.DataFrame(
            columns=['Date', 'Close', 'ticker']
        )
        
        for ticker in all_stocks:
            ticker_df = self.get_ystock_data_over_time(
                ticker
            )
            ticker_df.reset_index(inplace=True)
            ticker_df.rename(columns={'index': 'Date'}, inplace=True)
            ticker_df = ticker_df[['Date', 'Close', 'ticker']]
            stocks_df = pd.concat([stocks_df, ticker_df], ignore_index=True)
        
        stocks_df['pct_change'] = stocks_df.groupby('ticker')['Close'].pct_change()
        risk_df = (
            stocks_df
            .groupby('ticker')
            .agg(
                volatility = pd.NamedAgg('pct_change', 'std')
            )
            .reset_index()
        )
        min_volatility = risk_df['volatility'].min()
        max_volatility = risk_df['volatility'].max()
        risk_df['normalized_volatility'] = 10 * (risk_df['volatility'] - min_volatility) / (max_volatility - min_volatility)
        risk_df = risk_df.sort_values('normalized_volatility', ascending=False)
        
        gain_df = self.calculate_percentage_gain(stocks_df)
        
        if risk_level <= 4:
            recommended_stocks = (
                list(risk_df[risk_df['normalized_volatility']<=risk_level]
                .head(5)
                ['ticker'])
            )
        
        elif (risk_level > 4) and (risk_level < 8):
            recommended_stocks = (
                list(risk_df[
                    (risk_df['normalized_volatility']>4) &
                    (risk_df['normalized_volatility']<8)
                ]
                .head(5)
                ['ticker'])
            )
        
        else:
            recommended_stocks = (
                list(risk_df[risk_df['normalized_volatility']>=risk_level]
                .head(5)
                ['ticker'])
            )
            
        return {
            'recommended_stocks': recommended_stocks,
            'recent_gain': gain_df
        }
            
            
            
            
            
            
            
            
        
            
        
        