import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from plots.utils import set_plot_theme, color_palettes

# Try to import mplfinance. If it is available we will leverage its high-level API
# to draw the candlestick together with moving-average lines and a volume subplot.
try:
    import mplfinance as mpf
    from mplfinance.original_flavor import candlestick_ohlc  # still used for the low-level fallback
    MPLFINANCE_AVAILABLE = True
except ImportError:
    MPLFINANCE_AVAILABLE = False
    print("Warning: mplfinance not available. Using fallback candlestick implementation.")

def generate_stock_data(
    company: str = "Tesla",
    start_date: str = "2023-01-01",
    end_date: str = "2023-12-31",
    seed: Optional[int] = 42,
) -> Dict[str, List]:
    """
    Generate sample stock data for different companies.
    
    Parameters
    ----------
    company : str
        Company name to determine starting price and volatility
    start_date : str
        Start date in YYYY-MM-DD format
    end_date : str  
        End date in YYYY-MM-DD format
    seed : Optional[int]
        Random seed for reproducibility
        
    Returns
    -------
    Dict[str, List]
        Dictionary with OHLCV data
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Company-specific parameters
    company_params = {
        "Tesla": {"start_price": 200.0, "volatility": 0.025},
        "Apple": {"start_price": 150.0, "volatility": 0.020},
        "NVIDIA": {"start_price": 400.0, "volatility": 0.030},
        "Microsoft": {"start_price": 300.0, "volatility": 0.018},
        "Google": {"start_price": 2500.0, "volatility": 0.022},
        "Amazon": {"start_price": 120.0, "volatility": 0.024},
    }
    
    params = company_params.get(company, company_params["Tesla"])
    start_price = params["start_price"]
    volatility = params["volatility"]
    
    # Generate trading dates (weekdays only)
    all_dates = pd.date_range(start=start_date, end=end_date)
    trading_dates = all_dates[all_dates.dayofweek < 5]  # Monday to Friday
    dates = [d.strftime("%Y-%m-%d") for d in trading_dates]
    
    opens = []
    closes = []
    highs = []
    lows = []
    volumes = []
    
    current_price = start_price
    for i in range(len(dates)):
        if i == 0:
            opens.append(current_price)
        else:
            opens.append(closes[i - 1])
        
        # Generate price change with some drift
        price_change = np.random.normal(0, volatility * opens[i])
        
        # Add some mean reversion
        if opens[i] > start_price * 1.2:
            price_change -= volatility * opens[i] * 0.1
        elif opens[i] < start_price * 0.8:
            price_change += volatility * opens[i] * 0.1
        
        close = opens[i] + price_change
        closes.append(round(close, 2))
        
        # Generate high and low
        daily_range = abs(price_change) + (volatility * opens[i])
        high = max(opens[i], close) + abs(np.random.normal(0, daily_range / 3))
        low = min(opens[i], close) - abs(np.random.normal(0, daily_range / 3))
        
        highs.append(round(high, 2))
        lows.append(round(low, 2))
        
        # Generate volume
        base_volume = 1000000
        vol_factor = 1.0 + 2.0 * (abs(price_change) / (volatility * opens[i]))
        volume = int(base_volume * vol_factor * np.random.uniform(0.7, 1.3))
        volumes.append(volume)
    
    return {
        "Date": dates,
        "Open": opens,
        "High": highs,
        "Low": lows,
        "Close": closes,
        "Volume": volumes,
    }

def draw_candlestick_fallback(ax, ohlc_data, width=0.6, colorup="g", colordown="r"):
    """
    Fallback function to draw candlesticks when mplfinance is not available.
    """
    for i, (date_num, open_price, high, low, close) in enumerate(ohlc_data):
        # Determine color
        color = colorup if close >= open_price else colordown
        
        # Adjust line width based on candlestick width for better visibility
        line_width = max(1, width / 30) if width > 10 else 1
        
        # Draw the high-low line
        ax.plot([date_num, date_num], [low, high], color="black", linewidth=line_width)
        
        # Draw the open-close rectangle
        height = abs(close - open_price)
        bottom = min(open_price, close)
        
        rect = plt.Rectangle((date_num - width/2, bottom), width, height, 
                           facecolor=color, edgecolor="black", alpha=0.8, 
                           linewidth=line_width)
        ax.add_patch(rect)

def create_candlestick_plot(
    data_dict: Dict[str, List],
    company: str = "Tesla",
    theme: str = "Light",
    width: float = 0.6,
    colorup: str = "g",
    colordown: str = "r",
    timeframe: str = "Daily",
) -> plt.Axes:
    """
    Create a candlestick chart from OHLC data.
    
    Parameters
    ----------
    data_dict : Dict[str, List]
        Dictionary with OHLC data
    company : str
        Company name for the title
    theme : str
        Theme for the plot (Light/Dark)
    width : float
        Width of candlesticks
    colorup : str
        Color for up days
    colordown : str
        Color for down days
        
    Returns
    -------
    plt.Axes
        The axes object with the candlestick chart
    """
    # Validate data
    array_lengths = [len(arr) for arr in data_dict.values()]
    if len(set(array_lengths)) > 1:
        raise ValueError("All arrays in data_dict must be of the same length")
    
    df = pd.DataFrame(data_dict)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Date_num"] = df["Date"].apply(mdates.date2num)
    
    # Prepare OHLC data
    ohlc = df[["Date_num", "Open", "High", "Low", "Close"]].values
    
    #-----------------------------------------------------------------------------
    # If mplfinance is present use its high-level API to include
    #  • Moving-average (3, 6, 9)
    #  • A synced volume subplot (lower panel)
    #-----------------------------------------------------------------------------
    if MPLFINANCE_AVAILABLE:
        # mplfinance expects DateTimeIndex
        mpf_df = df.set_index("Date")[["Open", "High", "Low", "Close", "Volume"]]

        # Choose an mpf style consistent with the dashboard theme
        if theme == "Dark":
            mpf_style = mpf.make_mpf_style(base_mpf_style="nightclouds", rc={"axes.grid": True})
        else:
            mpf_style = mpf.make_mpf_style(base_mpf_style="yahoo", rc={"axes.grid": True})

        # Create the plot with volume and moving averages. We ask for figure so we
        # can integrate with MAIDR and the rest of the dashboard.
        fig, axes = mpf.plot(
            mpf_df,
            type="candle",
            mav=(3, 6, 9),
            volume=True,
            returnfig=True,
            style=mpf_style,
            ylabel="Price ($)",
            ylabel_lower="Volume",
            xlabel="Date",
            title=f"{company} Stock Price with Volume",
        )

        # Ensure overall theme matches dashboard selection
        # Apply to the primary price axis and figure background; volume axis will
        # inherit the facecolor from the mplfinance style which already obeys
        # the chosen theme.
        primary_ax = axes[0] if isinstance(axes, (list, tuple)) and len(axes) > 0 else axes
        set_plot_theme(fig, primary_ax, theme)
        fig.tight_layout()

        return primary_ax  # MAIDR will still capture the full figure via plt.gcf()

    #-----------------------------------------------------------------------------
    # Fallback: mplfinance is NOT available – draw manually as before
    #-----------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 6))
    set_plot_theme(fig, ax, theme)

    # For fallback, adjust width based on timeframe for better visibility
    fallback_width = width
    if timeframe == "Yearly":
        fallback_width = width * 3  # Make it even wider for fallback rendering
    elif timeframe == "Monthly":
        fallback_width = width * 2

    # Try using candlestick_ohlc from original_flavor if it exists
    if 'candlestick_ohlc' in globals():
        candlestick_ohlc(ax, ohlc, width=fallback_width, colorup=colorup, colordown=colordown, alpha=0.8)
    else:
        draw_candlestick_fallback(ax, ohlc, width=fallback_width, colorup=colorup, colordown=colordown)

    # Formatting
    ax.xaxis_date()
    if timeframe == "Daily":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
    elif timeframe == "Monthly":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
    elif timeframe == "Yearly":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha="center")

    ax.grid(True, linestyle="--", alpha=0.6)
    ax.set_title(f"{company} Stock Price - Candlestick Chart", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Price ($)", fontsize=12)

    plt.tight_layout()

    return ax

def aggregate_data_by_timeframe(data: Dict[str, List], timeframe: str) -> Dict[str, List]:
    """
    Aggregate daily data to monthly or yearly timeframes.
    
    Parameters
    ----------
    data : Dict[str, List]
        Daily OHLCV data
    timeframe : str
        'Daily', 'Monthly', or 'Yearly'
        
    Returns
    -------
    Dict[str, List]
        Aggregated OHLCV data
    """
    if timeframe == "Daily":
        return data
    
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"])
    
    if timeframe == "Monthly":
        # Group by month and year
        df['Period'] = df['Date'].dt.to_period('M')
        grouped = df.groupby('Period')
        
        aggregated_data = {
            'Date': [],
            'Open': [],
            'High': [],
            'Low': [],
            'Close': [],
            'Volume': []
        }
        
        for period, group in grouped:
            # Use the last day of the month as the date
            aggregated_data['Date'].append(period.end_time.strftime('%Y-%m-%d'))
            # First day's open price
            aggregated_data['Open'].append(group.iloc[0]['Open'])
            # Highest high in the month
            aggregated_data['High'].append(group['High'].max())
            # Lowest low in the month
            aggregated_data['Low'].append(group['Low'].min())
            # Last day's close price
            aggregated_data['Close'].append(group.iloc[-1]['Close'])
            # Sum of volumes
            aggregated_data['Volume'].append(group['Volume'].sum())
            
    elif timeframe == "Yearly":
        # Group by year
        df['Period'] = df['Date'].dt.to_period('Y')
        grouped = df.groupby('Period')
        
        aggregated_data = {
            'Date': [],
            'Open': [],
            'High': [],
            'Low': [],
            'Close': [],
            'Volume': []
        }
        
        for period, group in grouped:
            # Use December 31st as the date
            aggregated_data['Date'].append(period.end_time.strftime('%Y-%m-%d'))
            # First day's open price
            aggregated_data['Open'].append(group.iloc[0]['Open'])
            # Highest high in the year
            aggregated_data['High'].append(group['High'].max())
            # Lowest low in the year
            aggregated_data['Low'].append(group['Low'].min())
            # Last day's close price
            aggregated_data['Close'].append(group.iloc[-1]['Close'])
            # Sum of volumes
            aggregated_data['Volume'].append(group['Volume'].sum())
    
    return aggregated_data

def create_tutorial_candlestick_basics(theme="Light"):
    """
    Create a simple candlestick chart showing basic bullish and bearish candles
    for Module 1: Understanding the Building Blocks
    """
    import pandas as pd
    import os
    if MPLFINANCE_AVAILABLE:
        # Load sample data from CSV
        csv_path = os.path.join(os.path.dirname(__file__), '../sample_data/sample_candlestick.csv')
        df = pd.read_csv(csv_path, parse_dates=['Date'])
        df = df.sort_values('Date')
        df = df.set_index('Date')
        # Ensure correct dtypes
        for col in ['Open', 'High', 'Low', 'Close']:
            df[col] = df[col].astype(float)
        df['Volume'] = df['Volume'].astype(int)
        # Use only the first 5 rows for the tutorial
        mpf_df = df.iloc[:5]
        # Choose style based on theme
        if theme == "Dark":
            mpf_style = mpf.make_mpf_style(base_mpf_style="nightclouds", rc={"axes.grid": True})
        else:
            mpf_style = mpf.make_mpf_style(base_mpf_style="yahoo", rc={"axes.grid": True})
        fig, axes = mpf.plot(
            mpf_df,
            type="candle",
            mav=(3,),  # Simple 3-period moving average
            volume=True,
            returnfig=True,
            style=mpf_style,
            ylabel="Price ($)",
            ylabel_lower="Volume",
            xlabel="Date",
            title="Basic Candlestick Patterns: Bullish vs Bearish Candles",
        )
        primary_ax = axes[0] if isinstance(axes, (list, tuple)) and len(axes) > 0 else axes
        set_plot_theme(fig, primary_ax, theme)
        fig.tight_layout()
        return primary_ax
    else:
        # Fallback implementation
        fig, ax = plt.subplots(figsize=(10, 6))
        set_plot_theme(fig, ax, theme)
        ax.text(0.5, 0.5, "Tutorial: Basic Candlestick Patterns\n(mplfinance required)", 
                ha='center', va='center', transform=ax.transAxes)
        return ax

def create_tutorial_trends_volatility(theme="Light"):
    """
    Create candlestick chart showing uptrend, downtrend, and volatility patterns
    for Module 2: Reading the Market's Story
    This version forces the last 5 candles to be bearish and the moving average to slope down.
    """
    if MPLFINANCE_AVAILABLE:
        # Create 20-day dataset showing uptrend, then downtrend, then strong bearish finish
        dates = pd.date_range(start='2024-01-01', periods=20, freq='D')
        
        base_price = 100.0
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        
        for i in range(20):
            if i < 7:  # Uptrend
                trend_factor = 1.02 + (i * 0.01)
                volatility = 0.5
            elif i < 12:  # Downtrend
                trend_factor = 0.98 - ((i-7) * 0.01)
                volatility = 0.7
            elif i < 15:  # High volatility sideways
                trend_factor = 1.0
                volatility = 2.0
            else:  # Force strong bearish finish
                # Each day, open is previous close, close is much lower
                trend_factor = 0.95  # Strong drop
                volatility = 0.3
            
            if i == 0:
                opens.append(base_price)
            else:
                opens.append(closes[i-1])
            
            if i < 15:
                close = opens[i] * trend_factor + np.random.normal(0, volatility)
            else:
                # Force close to be much lower than open for last 5 candles
                close = opens[i] - abs(np.random.normal(2, 0.5)) - 2
            closes.append(close)
            
            high = max(opens[i], close) + abs(np.random.normal(0, volatility))
            low = min(opens[i], close) - abs(np.random.normal(0, volatility))
            highs.append(high)
            lows.append(low)
            
            # Volume increases with volatility
            if i >= 15:
                vol_multiplier = 2.0
            else:
                vol_multiplier = 1.0 + (volatility / 2.0)
            volumes.append(int(1000000 * vol_multiplier))
        
        data = {
            'Open': opens,
            'High': highs,
            'Low': lows,
            'Close': closes,
            'Volume': volumes
        }
        
        mpf_df = pd.DataFrame(data, index=dates)
        
        if theme == "Dark":
            mpf_style = mpf.make_mpf_style(base_mpf_style="nightclouds", rc={"axes.grid": True})
        else:
            mpf_style = mpf.make_mpf_style(base_mpf_style="yahoo", rc={"axes.grid": True})
        
        fig, axes = mpf.plot(
            mpf_df,
            type="candle",
            mav=(5, 10),  # Moving averages to show trend
            volume=True,
            returnfig=True,
            style=mpf_style,
            ylabel="Price ($)",
            ylabel_lower="Volume",
            xlabel="Date",
            title="Market Trends: Uptrend → Downtrend → Strong Bearish Finish",
        )
        
        primary_ax = axes[0] if isinstance(axes, (list, tuple)) and len(axes) > 0 else axes
        set_plot_theme(fig, primary_ax, theme)
        fig.tight_layout()
        
        return primary_ax
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        set_plot_theme(fig, ax, theme)
        ax.text(0.5, 0.5, "Tutorial: Trends and Volatility\n(mplfinance required)", 
                ha='center', va='center', transform=ax.transAxes)
        return ax

def create_tutorial_reversal_breakout(theme="Light"):
    """
    Create candlestick chart showing reversal and breakout patterns
    for Module 3: Basic Trading Concepts
    """
    if MPLFINANCE_AVAILABLE:
        # Create 15-day dataset showing reversal and breakout
        dates = pd.date_range(start='2024-01-01', periods=15, freq='D')
        
        # Craft data to show downtrend, reversal, then breakout
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        
        base_price = 110.0
        
        for i in range(15):
            if i < 6:  # Downtrend
                trend_factor = 0.98 - (i * 0.005)
                volatility = 0.8
            elif i < 9:  # Reversal formation
                trend_factor = 1.001 + (i-6) * 0.002
                volatility = 1.2
            else:  # Breakout upward
                trend_factor = 1.03 + (i-9) * 0.01
                volatility = 0.6
            
            if i == 0:
                opens.append(base_price)
            else:
                opens.append(closes[i-1])
            
            close = opens[i] * trend_factor + np.random.normal(0, volatility)
            closes.append(close)
            
            high = max(opens[i], close) + abs(np.random.normal(0, volatility))
            low = min(opens[i], close) - abs(np.random.normal(0, volatility))
            
            highs.append(high)
            lows.append(low)
            
            # Volume increases during reversal and breakout
            if 6 <= i <= 9:  # Reversal period
                vol_multiplier = 1.5
            elif i >= 10:  # Breakout period
                vol_multiplier = 2.0
            else:
                vol_multiplier = 1.0
                
            volumes.append(int(1000000 * vol_multiplier))
        
        data = {
            'Open': opens,
            'High': highs,
            'Low': lows,
            'Close': closes,
            'Volume': volumes
        }
        
        mpf_df = pd.DataFrame(data, index=dates)
        
        if theme == "Dark":
            mpf_style = mpf.make_mpf_style(base_mpf_style="nightclouds", rc={"axes.grid": True})
        else:
            mpf_style = mpf.make_mpf_style(base_mpf_style="yahoo", rc={"axes.grid": True})
        
        fig, axes = mpf.plot(
            mpf_df,
            type="candle",
            mav=(5, 10),
            volume=True,
            returnfig=True,
            style=mpf_style,
            ylabel="Price ($)",
            ylabel_lower="Volume",
            xlabel="Date",
            title="Reversal and Breakout Pattern",
        )
        
        primary_ax = axes[0] if isinstance(axes, (list, tuple)) and len(axes) > 0 else axes
        set_plot_theme(fig, primary_ax, theme)
        fig.tight_layout()
        
        return primary_ax
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        set_plot_theme(fig, ax, theme)
        ax.text(0.5, 0.5, "Tutorial: Reversal and Breakout\n(mplfinance required)", 
                ha='center', va='center', transform=ax.transAxes)
        return ax

def create_tutorial_hammer_pattern(theme="Light"):
    """
    Create candlestick chart showing hammer reversal pattern
    for Module 4: Basic Trading Strategies - Hammer
    """
    if MPLFINANCE_AVAILABLE:
        # Create 10-day dataset with clear hammer pattern
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        
        base_price = 100.0
        
        for i in range(10):
            if i < 6:  # Downtrend leading to hammer
                trend_factor = 0.97 - (i * 0.01)
                volatility = 0.5
            elif i == 6:  # Hammer day
                # Hammer: small body at top, long lower wick
                opens.append(closes[i-1] if i > 0 else base_price * 0.9)
                closes.append(opens[i] + 0.5)  # Small body
                lows.append(opens[i] - 3.0)  # Long lower wick
                highs.append(opens[i] + 0.8)  # Small upper wick
                volumes.append(1500000)  # High volume
                continue
            else:  # Confirmation and recovery
                trend_factor = 1.02 + (i-7) * 0.01
                volatility = 0.8
            
            if i == 0:
                opens.append(base_price)
            elif i != 6:
                opens.append(closes[i-1])
            
            if i != 6:
                close = opens[i] * trend_factor + np.random.normal(0, volatility)
                closes.append(close)
                
                high = max(opens[i], close) + abs(np.random.normal(0, volatility))
                low = min(opens[i], close) - abs(np.random.normal(0, volatility))
                
                highs.append(high)
                lows.append(low)
                
                vol_multiplier = 1.2 if i > 6 else 1.0
                volumes.append(int(1000000 * vol_multiplier))
        
        data = {
            'Open': opens,
            'High': highs,
            'Low': lows,
            'Close': closes,
            'Volume': volumes
        }
        
        mpf_df = pd.DataFrame(data, index=dates)
        
        if theme == "Dark":
            mpf_style = mpf.make_mpf_style(base_mpf_style="nightclouds", rc={"axes.grid": True})
        else:
            mpf_style = mpf.make_mpf_style(base_mpf_style="yahoo", rc={"axes.grid": True})
        
        fig, axes = mpf.plot(
            mpf_df,
            type="candle",
            mav=(5,),
            volume=True,
            returnfig=True,
            style=mpf_style,
            ylabel="Price ($)",
            ylabel_lower="Volume",
            xlabel="Date",
            title="Hammer Reversal Pattern (Day 7)",
        )
        
        primary_ax = axes[0] if isinstance(axes, (list, tuple)) and len(axes) > 0 else axes
        set_plot_theme(fig, primary_ax, theme)
        fig.tight_layout()
        
        return primary_ax
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        set_plot_theme(fig, ax, theme)
        ax.text(0.5, 0.5, "Tutorial: Hammer Reversal Pattern\n(mplfinance required)", 
                ha='center', va='center', transform=ax.transAxes)
        return ax

def create_tutorial_shooting_star_pattern(theme="Light"):
    """
    Create candlestick chart showing shooting star reversal pattern
    for Module 4: Basic Trading Strategies - Shooting Star
    """
    if MPLFINANCE_AVAILABLE:
        # Create 10-day dataset with clear shooting star pattern
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        
        base_price = 100.0
        
        for i in range(10):
            if i < 6:  # Uptrend leading to shooting star
                trend_factor = 1.02 + (i * 0.01)
                volatility = 0.5
            elif i == 6:  # Shooting star day
                # Shooting star: small body at bottom, long upper wick
                opens.append(closes[i-1] if i > 0 else base_price * 1.1)
                closes.append(opens[i] - 0.5)  # Small body (bearish)
                highs.append(opens[i] + 3.0)  # Long upper wick
                lows.append(opens[i] - 0.8)  # Small lower wick
                volumes.append(1500000)  # High volume
                continue
            else:  # Confirmation and decline
                trend_factor = 0.98 - (i-7) * 0.01
                volatility = 0.8
            
            if i == 0:
                opens.append(base_price)
            elif i != 6:
                opens.append(closes[i-1])
            
            if i != 6:
                close = opens[i] * trend_factor + np.random.normal(0, volatility)
                closes.append(close)
                
                high = max(opens[i], close) + abs(np.random.normal(0, volatility))
                low = min(opens[i], close) - abs(np.random.normal(0, volatility))
                
                highs.append(high)
                lows.append(low)
                
                vol_multiplier = 1.2 if i > 6 else 1.0
                volumes.append(int(1000000 * vol_multiplier))
        
        data = {
            'Open': opens,
            'High': highs,
            'Low': lows,
            'Close': closes,
            'Volume': volumes
        }
        
        mpf_df = pd.DataFrame(data, index=dates)
        
        if theme == "Dark":
            mpf_style = mpf.make_mpf_style(base_mpf_style="nightclouds", rc={"axes.grid": True})
        else:
            mpf_style = mpf.make_mpf_style(base_mpf_style="yahoo", rc={"axes.grid": True})
        
        fig, axes = mpf.plot(
            mpf_df,
            type="candle",
            mav=(5,),
            volume=True,
            returnfig=True,
            style=mpf_style,
            ylabel="Price ($)",
            ylabel_lower="Volume",
            xlabel="Date",
            title="Shooting Star Reversal Pattern (Day 7)",
        )
        
        primary_ax = axes[0] if isinstance(axes, (list, tuple)) and len(axes) > 0 else axes
        set_plot_theme(fig, primary_ax, theme)
        fig.tight_layout()
        
        return primary_ax
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        set_plot_theme(fig, ax, theme)
        ax.text(0.5, 0.5, "Tutorial: Shooting Star Reversal Pattern\n(mplfinance required)", 
                ha='center', va='center', transform=ax.transAxes)
        return ax

def create_candlestick(company, timeframe, theme):
    """
    Create a candlestick plot based on company selection, timeframe, and theme.
    This function follows the pattern used by other plot modules in the project.
    
    MAIDR INTEGRATION NOTE:
    MAIDR is currently commented out in app.py to ensure the plot renders properly.
    When MAIDR is working, you can uncomment the @render_maidr decorator 
    and comment out the manual SVG rendering in app.py.
    """
    import pandas as pd
    import os
    # For 'Daily' timeframe, load from CSV
    if timeframe == "Daily":
        csv_path = os.path.join(os.path.dirname(__file__), '../sample_data/sample_candlestick.csv')
        df = pd.read_csv(csv_path, parse_dates=['Date'])
        df = df.sort_values('Date')
        df = df.set_index('Date')
        for col in ['Open', 'High', 'Low', 'Close']:
            df[col] = df[col].astype(float)
        df['Volume'] = df['Volume'].astype(int)
        data = {
            'Date': df.index.strftime('%Y-%m-%d').tolist(),
            'Open': df['Open'].tolist(),
            'High': df['High'].tolist(),
            'Low': df['Low'].tolist(),
            'Close': df['Close'].tolist(),
            'Volume': df['Volume'].tolist(),
        }
    else:
        # Use one year of data for monthly/yearly views (keep old logic)
        data = generate_stock_data(
            company=company,
            start_date="2023-01-01", 
            end_date="2023-12-31",
            seed=42
        )
    
    # Aggregate data based on timeframe
    aggregated_data = aggregate_data_by_timeframe(data, timeframe)
    
    # Adjust candlestick width based on timeframe
    if timeframe == "Daily":
        width = 0.6
    elif timeframe == "Monthly":
        width = 25  # Wider for monthly data (fewer points)
    elif timeframe == "Yearly":
        width = 200  # Much wider for yearly data (very few points) - about 6-7 months width
    
    # Create the candlestick plot
    title_suffix = f" - {timeframe} View"
    ax = create_candlestick_plot(
        aggregated_data, 
        company=company + title_suffix, 
        theme=theme,
        timeframe=timeframe,
        width=width
    )
    
    return ax 