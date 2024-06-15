# ----- Imports -----
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
        end_date='yesterday'
    ):
        """
        """
        today = datetime.today()
        
        if end_date in ['', 'yesterday', 'y']:
            end_date = today + relativedelta(days=-1)
        
        if start_date in ['', 'yesterday', 'y', None]:
            start_date = end_date + relativedelta(days=-30)
        
        df = yf.download(ticker, start=start_date, end=end_date)
        df['ticker'] = [ticker] * len(df)
        return df
    
    def calculate_percentage_gain(
        self,
        df,
        scope='stock',
        interval='daily'
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
                ['Close']
                .pct_change() * 100
            )
            gain_df = gain_df.dropna(subset=['pct_change'])
        
        return gain_df
            
            
            
            
        
            
        
        