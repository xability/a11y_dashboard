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

def create_custom_barplot(df, var_x, var_y, color, theme):
    """Create a bar plot from pre-aggregated user data (x=category, y=value)."""
    if not var_x or not var_y or df is None:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax, theme)
    sns.barplot(data=df, x=var_x, y=var_y, ax=ax, color=color)
    ax.set_title(f"{var_x} vs {var_y}")
    ax.set_xlabel(var_x.replace("_", " ").title())
    ax.set_ylabel(var_y.replace("_", " ").title())

    return ax


def create_custom_countplot(df, var, color, theme):
    """Create a count plot from raw data – automatically counts frequency of each category."""
    if not var or df is None:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax, theme)
    sns.countplot(data=df, x=var, color=color, ax=ax)
    ax.set_title(f"Count of {var.replace('_', ' ').title()}")
    ax.set_xlabel(var.replace("_", " ").title())
    ax.set_ylabel("Count")

    return ax