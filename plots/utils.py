import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

def set_plot_theme(fig, ax, theme):
    """Apply the appropriate theme to a plot"""
    if theme == "Dark":
        plt.style.use("dark_background")
        fig.patch.set_facecolor("#2E2E2E")
        ax.set_facecolor("#2E2E2E")
    else:
        plt.style.use("default")
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        
# Dictionary of color palettes
color_palettes = {
    "Default": "#007bc2",
    "Red": "#FF0000",
    "Green": "#00FF00",
    "Blue": "#0000FF",
    "Purple": "#800080",
    "Orange": "#FFA500",
}