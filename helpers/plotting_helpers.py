# ----- Imports -----
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

from data.configs import STOCK_TICKERS_DICT

from helpers.data_manipulation_helpers import DataManipulationHelpers

dmh__i = DataManipulationHelpers()

# ----- PlottingHelpers -----
class PlottingHelpers():
    """
    """
    def __init__(self):
        """
        """
        pass
    
    def plot_stock_decomposition(
        self,
        decomposition,
        ticker
    ):
        """
        """
        # creating the subplots
        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            subplot_titles=(
                f"Stock Price",
                f"Stock Trend",
                f"Stock Cyclical Behavior",
            )
        )
        # adding the trend
        fig.add_trace(
            go.Scatter(
                x=decomposition.observed.index,
                y=decomposition.observed
            ),
            row=1,
            col=1
        )
        
        # adding the trend
        fig.add_trace(
            go.Scatter(
                x=decomposition.trend.index,
                y=decomposition.trend
            ),
            row=2,
            col=1
        )
        
        # adding the seasonality
        fig.add_trace(
            go.Scatter(
                x=decomposition.seasonal.index,
                y=decomposition.seasonal
            ),
            row=3,
            col=1
        )
        
        fig.update_layout(
            height=950,
            width=1000,
            showlegend=False,
            title_text=f"{STOCK_TICKERS_DICT[ticker]}'s Stock Decomposition"
        )
        
        fig.update_xaxes(title_text='Date')
        fig.update_yaxes(title_text='Price', row=1, col=1)
        fig.update_yaxes(title_text='Trend', row=2, col=1)
        fig.update_yaxes(title_text='Cyclical Behavior', row=3, col=1)
        return fig
