import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from plots.utils import set_plot_theme, color_palettes

def create_boxplot(input_boxplot_type, input_boxplot_color, theme):
    """Create a box plot based on input parameters"""
    boxplot_type = input_boxplot_type
    color = color_palettes[input_boxplot_color]

    # Generate data based on the selected box plot type
    if boxplot_type == "Positively Skewed with Outliers":
        data = np.random.lognormal(mean=0, sigma=0.5, size=1000)
    elif boxplot_type == "Negatively Skewed with Outliers":
        data = -np.random.lognormal(mean=0, sigma=0.5, size=1000)
    elif boxplot_type == "Symmetric with Outliers":
        data = np.random.normal(loc=0, scale=1, size=1000)
    elif boxplot_type == "Symmetric without Outliers":
        data = np.random.normal(loc=0, scale=1, size=1000)
        data = data[(data > -1.5) & (data < 1.5)]  # Strict range to avoid outliers
    else:
        data = np.random.normal(loc=0, scale=1, size=1000)

    # Create the plot using matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax, theme)
    sns.boxplot(x=data, ax=ax, color=color)  # Horizontal box plot
    ax.set_title(f"{boxplot_type}")
    ax.set_xlabel("Value")

    return ax

def create_custom_boxplot(df, var_x, var_y, color, theme):
    """Create a box plot from user data"""
    if df is None:
        return None
        
    fig, ax = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax, theme)
    
    if var_x and var_y:
        sns.boxplot(x=var_y, y=var_x, data=df, palette=[color], ax=ax)
        ax.set_title(f"{var_x} grouped by {var_y}")
        ax.set_xlabel(var_y.replace("_", " ").title())
        ax.set_ylabel(var_x.replace("_", " ").title())
    elif var_x:
        sns.boxplot(y=df[var_x], color=color, ax=ax)
        ax.set_title(f"{var_x}")
        ax.set_ylabel(var_x.replace("_", " ").title())
    else:
        return None
        
    return ax