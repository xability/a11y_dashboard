import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from plots.utils import set_plot_theme

def generate_multiline_data(multiline_type):
    """Generate data for multiline plots based on the selected type"""
    x = np.linspace(0, 10, 30)  # 30 points for x-axis
    series_names = ["Series 1", "Series 2", "Series 3"]
    
    if multiline_type == "Simple Trends":
        # Linear trends with different slopes
        y1 = 1.5 * x + np.random.normal(0, 1, 30)
        y2 = 0.5 * x + 5 + np.random.normal(0, 1, 30)
        y3 = -x + 15 + np.random.normal(0, 1, 30)
    elif multiline_type == "Seasonal Patterns":
        # Sinusoidal patterns with different phases
        y1 = 5 * np.sin(x) + 10 + np.random.normal(0, 0.5, 30)
        y2 = 5 * np.sin(x + np.pi/2) + 10 + np.random.normal(0, 0.5, 30)
        y3 = 5 * np.sin(x + np.pi) + 10 + np.random.normal(0, 0.5, 30)
    elif multiline_type == "Growth Comparison":
        # Different growth patterns
        y1 = np.exp(0.2 * x) + np.random.normal(0, 0.5, 30)
        y2 = x**2 / 10 + np.random.normal(0, 1, 30)
        y3 = np.log(x + 1) * 5 + np.random.normal(0, 0.5, 30)
    else:  # Random Series
        # Random walks with different volatilities
        y1 = np.cumsum(np.random.normal(0, 0.5, 30))
        y2 = np.cumsum(np.random.normal(0.1, 0.7, 30))
        y3 = np.cumsum(np.random.normal(-0.05, 0.9, 30))
    
    # Create a dataframe with the generated data
    return pd.DataFrame({
        "x": np.tile(x, 3),
        "y": np.concatenate([y1, y2, y3]),
        "series": np.repeat(series_names, len(x))
    })

def create_multiline_plot(data, input_multiline_type, input_multiline_color, theme):
    """Create a multiline plot based on input parameters and data"""
    multiline_type = input_multiline_type
    palette = input_multiline_color
    
    # Map friendly palette names to seaborn palette names
    palette_mapping = {
        "Default": None,  # Use default seaborn palette
        "Colorful": "Set1",
        "Pastel": "Set2",
        "Dark Tones": "Dark2",
        "Paired Colors": "Paired",
        "Rainbow": "Spectral"
    }
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax, theme)
    
    # Use seaborn lineplot for multiple lines
    if palette == "Default":
        # Use default seaborn color palette
        sns.lineplot(
            x="x", y="y", hue="series", style="series", 
            markers=True, dashes=True, data=data, ax=ax
        )
    else:
        # Use selected color palette
        sns.lineplot(
            x="x", y="y", hue="series", style="series", 
            markers=True, dashes=True, data=data, ax=ax,
            palette=palette_mapping[palette]
        )
    
    # Customize the plot
    ax.set_title(f"Multiline Plot: {multiline_type}")
    ax.set_xlabel("X values")
    ax.set_ylabel("Y values")
    
    return ax

def create_custom_multiline_plot(df, var_x, var_y, var_group, palette, theme):
    """Create a multiline plot from user data"""
    if not var_x or not var_y or not var_group or df is None:
        return None
    
    # Map friendly palette names to seaborn palette names
    palette_mapping = {
        "Default": None,  # Use default seaborn palette
        "Colorful": "Set1",
        "Pastel": "Set2",
        "Dark Tones": "Dark2",
        "Paired Colors": "Paired",
        "Rainbow": "Spectral"
    }
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax, theme)
    
    # Use seaborn lineplot for multiple lines
    if palette == "Default":
        # Use default seaborn color palette
        sns.lineplot(
            x=var_x, y=var_y, hue=var_group, style=var_group, 
            markers=True, dashes=True, data=df, ax=ax
        )
    else:
        # Use selected color palette
        sns.lineplot(
            x=var_x, y=var_y, hue=var_group, style=var_group, 
            markers=True, dashes=True, data=df, ax=ax,
            palette=palette_mapping[palette]
        )
    
    # Customize the plot
    ax.set_title(f"{var_y} vs {var_x} by {var_group}")
    ax.set_xlabel(var_x.replace("_", " ").title())
    ax.set_ylabel(var_y.replace("_", " ").title())
    
    return ax