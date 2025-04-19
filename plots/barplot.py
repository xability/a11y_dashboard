import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from plots.utils import set_plot_theme, color_palettes

def create_barplot(input_barplot_color, theme):
    """Create a bar plot based on input parameters"""
    color = color_palettes[input_barplot_color]
    categories = ["Category A", "Category B", "Category C", "Category D", "Category E"]
    values = np.random.randint(10, 100, size=5)

    fig, ax = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax, theme)
    sns.barplot(x=categories, y=values, ax=ax, color=color)
    ax.set_title("Plot of Categories")
    ax.set_xlabel("Categories")
    ax.set_ylabel("Values")

    return ax

def create_custom_barplot(df, var, color, theme):
    """Create a bar plot from user data"""
    if not var or df is None:
        return None
        
    fig, ax = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax, theme)
    sns.countplot(data=df, x=var, color=color, ax=ax)
    ax.set_title(f"{var}")
    ax.set_xlabel(var.replace("_", " ").title())
    ax.set_ylabel("Count")
    
    return ax