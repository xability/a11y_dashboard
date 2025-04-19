import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from plots.utils import set_plot_theme, color_palettes

def create_lineplot(input_lineplot_type, input_lineplot_color, theme):
    """Create a line plot based on input parameters"""
    lineplot_type = input_lineplot_type
    color = color_palettes[input_lineplot_color]

    x = np.linspace(0, 10, 20)  # Reduced number of points
    if lineplot_type == "Linear Trend":
        y = 2 * x + 1 + np.random.normal(0, 1, 20)
    elif lineplot_type == "Exponential Growth":
        y = np.exp(0.5 * x) + np.random.normal(0, 1, 20)
    elif lineplot_type == "Sinusoidal Pattern":
        y = 5 * np.sin(x) + np.random.normal(0, 0.5, 20)
    elif lineplot_type == "Random Walk":
        y = np.cumsum(np.random.normal(0, 1, 20))
    else:
        y = x + np.random.normal(0, 1, 20)

    fig, ax = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax, theme)
    sns.lineplot(x=x, y=y, ax=ax, color=color)
    ax.set_title(f"{lineplot_type}")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    return ax

def create_custom_lineplot(df, var_x, var_y, color, theme):
    """Create a line plot from user data"""
    if not var_x or not var_y or df is None:
        return None
        
    fig, ax = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax, theme)
    sns.lineplot(data=df, x=var_x, y=var_y, color=color, ax=ax)
    ax.set_title(f"{var_y} vs {var_x}")
    ax.set_xlabel(var_x.replace("_", " ").title())
    ax.set_ylabel(var_y.replace("_", " ").title())
    
    return ax