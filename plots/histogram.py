import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from plots.utils import set_plot_theme, color_palettes

def create_histogram(input_distribution_type, input_hist_color, theme):
    """Create a histogram based on input parameters"""
    distribution_type = input_distribution_type
    color = color_palettes[input_hist_color]

    # Generate data based on the selected distribution
    if distribution_type == "Normal Distribution":
        data = np.random.normal(size=1000)
    elif distribution_type == "Positively Skewed":
        data = np.random.exponential(scale=3, size=1000)
    elif distribution_type == "Negatively Skewed":
        data = -np.random.exponential(scale=1.5, size=1000)
    elif distribution_type == "Unimodal Distribution":
        data = np.random.normal(loc=0, scale=2.5, size=1000)
    elif distribution_type == "Bimodal Distribution":
        data = np.concatenate(
            [
                np.random.normal(-2, 0.5, size=500),
                np.random.normal(2, 0.5, size=500),
            ]
        )
    elif distribution_type == "Multimodal Distribution":
        data = np.concatenate(
            [
                np.random.normal(-2, 0.5, size=300),
                np.random.normal(2, 0.5, size=300),
                np.random.normal(5, 0.5, size=400),
            ]
        )
    else:
        data = np.random.normal(size=1000)

    # Create the plot using matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax, theme)
    sns.histplot(data, kde=True, bins=20, color=color, edgecolor="white", ax=ax)
    ax.set_title(f"{distribution_type}")
    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")

    return ax
    
def create_custom_histogram(df, var, color, theme):
    """Create a histogram from user data"""
    if not var or df is None:
        return None
        
    fig, ax = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax, theme)
    sns.histplot(data=df, x=var, kde=True, color=color, ax=ax)
    ax.set_title(f"{var}")
    ax.set_xlabel(var.replace("_", " ").title())
    ax.set_ylabel("Count")
    
    return ax