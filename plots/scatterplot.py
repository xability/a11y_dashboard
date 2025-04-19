import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from plots.utils import set_plot_theme, color_palettes

def create_scatterplot(input_scatterplot_type, input_scatter_color, theme):
    """Create a scatter plot based on input parameters"""
    scatterplot_type = input_scatterplot_type
    color = color_palettes[input_scatter_color]

    num_points = np.random.randint(20, 31)  # Randomly select between 20 and 30 points
    if scatterplot_type == "No Correlation":
        x = np.random.uniform(size=num_points)
        y = np.random.uniform(size=num_points)
    elif scatterplot_type == "Weak Positive Correlation":
        x = np.random.uniform(size=num_points)
        y = 0.3 * x + np.random.uniform(size=num_points)
    elif scatterplot_type == "Strong Positive Correlation":
        x = np.random.uniform(size=num_points)
        y = 0.9 * x + np.random.uniform(size=num_points) * 0.1
    elif scatterplot_type == "Weak Negative Correlation":
        x = np.random.uniform(size=num_points)
        y = -0.3 * x + np.random.uniform(size=num_points)
    elif scatterplot_type == "Strong Negative Correlation":
        x = np.random.uniform(size=num_points)
        y = -0.9 * x + np.random.uniform(size=num_points) * 0.1
    else:
        x = np.random.uniform(size=num_points)
        y = np.random.uniform(size=num_points)

    # Create the plot using matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax, theme)
    sns.scatterplot(x=x, y=y, ax=ax, color=color)
    ax.set_title(f"{scatterplot_type}")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    return ax

def create_custom_scatterplot(df, var_x, var_y, color, theme):
    """Create a scatter plot from user data"""
    if not var_x or not var_y or df is None:
        return None
        
    fig, ax = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax, theme)
    sns.scatterplot(data=df, x=var_x, y=var_y, color=color, ax=ax)
    ax.set_title(f"{var_y} vs {var_x}")
    ax.set_xlabel(var_x.replace("_", " ").title())
    ax.set_ylabel(var_y.replace("_", " ").title())
    
    return ax