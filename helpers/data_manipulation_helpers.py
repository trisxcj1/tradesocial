# ----- Imports -----
import pandas as pd
import numpy as np

from datetime import datetime
from dateutil.relativedelta import relativedelta

import joblib
import os
from dotenv import load_dotenv

import yfinance as yf

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

from scipy.spatial.distance import cdist

from statsmodels.tsa.seasonal import seasonal_decompose

from data.configs import STOCK_TICKERS_DICT

# ----- DataManipulationHelpers -----

load_dotenv()
FY_MODEL = os.getenv('FY_MODEL_LOCATION')

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
    
    def claculate_fy_recommended_stocks(
        self,
        risk_level,
    ):
        """
        """
        fy_model = joblib.load(FY_MODEL)
        all_stocks = list(STOCK_TICKERS_DICT.keys())
        stocks_df = pd.DataFrame(
            columns=['Date', 'Close', 'Volume', 'ticker']
        )
        
        for ticker in all_stocks:
            ticker_df = self.get_ystock_data_over_time(
                ticker,
                start_date='most recent trading day',
                end_date='most recent trading day'
            )
            ticker_df.reset_index(inplace=True)
            ticker_df.rename(columns={'index': 'Date'}, inplace=True)
            ticker_df = ticker_df[['Date', 'Close', 'Volume', 'ticker']]
            stocks_df = pd.concat([stocks_df, ticker_df], ignore_index=True)
        
        predictions = fy_model.predict(stocks_df[['Close', 'Volume']])
        probabilities = fy_model.predict_proba(stocks_df[['Close', 'Volume']])
        
        stocks_df['prediction'] = predictions
        stocks_df['probability'] = probabilities.max(axis=1)
        recommended_buys = stocks_df[stocks_df['prediction']==True].sort_values('probability', ascending=False)
        recommended_sells = stocks_df[stocks_df['prediction']==False].sort_values('probability', ascending=False)

        return {
            'recommended_stocks': {
                'buys': recommended_buys,
                'sells': recommended_sells
            }
        }
        
    def calculate_ymal_recommended_stocks(
        self,
        risk_level
    ):
        """
        """
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
            risk_msg = """
            Given your risk level, here are a few stocks that have relatively low volatility.
            Low volatility means that the stock price for these companies change over time, but
            the difference in day-to-day change is relatively consistent over time.
            
            These stocks should allow you to minimize risk as much as possible,
            while still allowing you to increase the value of your portfolio. 
            """
            recommended_stocks = (
                list(risk_df[risk_df['normalized_volatility']<=risk_level]
                .head(4)
                ['ticker'])
            )
        
        elif (risk_level > 4) and (risk_level < 8):
            recommended_stocks = (
                list(risk_df[
                    (risk_df['normalized_volatility']>4) &
                    (risk_df['normalized_volatility']<8)
                ]
                .head(4)
                ['ticker'])
            )
            risk_msg = """
            Given your risk level, here's a blend of stocks that offer a mix of volatility.
            Volatility means that the stock price for these companies change over time, and the magnitude
            of these changes can also be quite different.
            
            These stocks offer you the opportunity to capitalize on favorable uncertainty in the market,
            while still being relatively conservative.
            """
        
        else:
            recommended_stocks = (
                list(risk_df[risk_df['normalized_volatility']>=risk_level]
                .head(4)
                ['ticker'])
            )
            risk_msg = """
            Given your risk level, here's a list of stocks that have high volatility.
            High volatility means that the stock price for these companies experience big swings day-to-day,
            and these stocks carry relatively high risk.
            
            These stocks give you a high chance of winning big since high risks means high rewards.
            Remember that risk works both ways. Therefore, if you can win big, you can
            also lose big -- never invest more than you're willing to lose.
            """
            
        return {
            'risk_msg': risk_msg,
            'recommended_stocks': recommended_stocks,
            'recent_gain': gain_df
        }
        
    def calculate_similarity(
        self
    ):
        """
        """
        scaler = StandardScaler()
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
            
        stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])
        stocks_df['pct_change'] = stocks_df.groupby('ticker')['Close'].pct_change()
        stocks_df.dropna(subset=['pct_change'], inplace=True)
        
        stocks_df['features'] = list(
            zip(
                stocks_df['Close'],
                stocks_df['pct_change']
            )
        )
        
        grouped_features = stocks_df.groupby('ticker')['features'].apply(list)
        
        normalized_features = {}
        for ticker, features in grouped_features.items():
            normalized_features[ticker] = scaler.fit_transform(features)

        normalized_features_list = [normalized_features[ticker] for ticker in all_stocks]
        reshaped_features = [feat.flatten() for feat in normalized_features_list]
        
        similarity_matrix = cosine_similarity(
            np.array(
                reshaped_features
            )
        )
        similarity_df = pd.DataFrame(
            similarity_matrix,
            columns=grouped_features.keys(),
            index=grouped_features.keys()
        )
        return similarity_df
    
    def calculate_ts_decomposition(
        self,
        data,
        ticker,
        decomp_value='Close'
    ):
        """
        """
        # setting Date as the index if not already done
        # if 'Date' in data.columns:
        #     data = data.set_index('Date')
        data = data[data['ticker']==ticker]
        data_by_date = data.set_index('Date')
        data_by_date = data_by_date.sort_index()
        
        decomposition = seasonal_decompose(
            data_by_date[decomp_value],
            model='multiplicative',
            period=252
        )
        return decomposition
    
    def generate_sesonality_information(
        self,
        decomposition
    ):
        """
        """
        crossings = []
        days_between_crossings = []
        seasonal = decomposition.seasonal
        seasonal_mean = seasonal.mean()
        
        seasonal_df = seasonal.reset_index()
        seasonal_df['month'] = seasonal_df['Date'].dt.month
        seasonal_df['year'] = seasonal_df['Date'].dt.year
        
        typical_peak_month = (
            seasonal_df
            .groupby('year')
            .apply(lambda x: x.loc[x['seasonal'].idxmax()]['month'])[:-1].mean()
        )
        typical_trough_month = (
            seasonal_df
            .groupby('year')
            .apply(lambda x: x.loc[x['seasonal'].idxmin()]['month'])[:-1].mean()
        )
        
        for i in range(1, len(seasonal)):
            if (
                ((seasonal[i-1] < seasonal_mean) and (seasonal[i] > seasonal_mean)) or
                ((seasonal[i-1] > seasonal_mean) and (seasonal[i] < seasonal_mean))
            ):
                crossings.append(seasonal.index[i])
        
        for i in range(1, len(crossings)):
            days_between = (crossings[i] - crossings[i-1]).days
            if days_between > 62:
                days_between_crossings.append(days_between)
        
        
        
        estimated_cycle_length = (np.mean(days_between_crossings)) * 2
        output = {
            'seasonal_mean': seasonal_mean,
            'typical_peak_month': typical_peak_month + 0.001,
            'typical_trough_month': typical_trough_month + 0.001,
            'estimated_cycle_length': estimated_cycle_length
        }
        return output
