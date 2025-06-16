import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from plots.utils import set_plot_theme, color_palettes

# Try to import mplfinance, if not available use a fallback
try:
    from mplfinance.original_flavor import candlestick_ohlc
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
    
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(12, 6))
    set_plot_theme(fig, ax, theme)
    
    # Plot candlesticks
    if MPLFINANCE_AVAILABLE:
        # mplfinance uses width in data units (days)
        candlestick_ohlc(ax, ohlc, width=width, colorup=colorup, colordown=colordown, alpha=0.8)
    else:
        # For fallback, adjust width based on timeframe for better visibility
        fallback_width = width
        if timeframe == "Yearly":
            fallback_width = width * 3  # Make it even wider for fallback rendering
        elif timeframe == "Monthly":
            fallback_width = width * 2
        draw_candlestick_fallback(ax, ohlc, width=fallback_width, colorup=colorup, colordown=colordown)
    
    # Format the plot based on timeframe
    ax.xaxis_date()
    
    if timeframe == "Daily":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    elif timeframe == "Monthly":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    elif timeframe == "Yearly":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')
    
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.set_title(f"{company} Stock Price - Candlestick Chart", fontsize=14, fontweight='bold')
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

def create_candlestick(company, timeframe, theme):
    """
    Create a candlestick plot based on company selection, timeframe, and theme.
    This function follows the pattern used by other plot modules in the project.
    
    MAIDR INTEGRATION NOTE:
    MAIDR is currently commented out in app.py to ensure the plot renders properly.
    When MAIDR is working, you can uncomment the @render_maidr decorator 
    and comment out the manual SVG rendering in app.py.
    """
    # Generate data for the selected company
    if timeframe == "Yearly":
        # Generate multiple years of data for yearly view
        data = generate_stock_data(
            company=company,
            start_date="2018-01-01", 
            end_date="2023-12-31",
            seed=42
        )
    else:
        # Use one year of data for daily and monthly views
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