import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from plots.utils import set_plot_theme

def create_heatmap(input_heatmap_type, theme):
    """Create a heatmap based on input parameters"""
    heatmap_type = input_heatmap_type

    if heatmap_type == "Random":
        data = np.random.rand(5, 5)  # Reduced size
    elif heatmap_type == "Correlated":
        data = np.random.multivariate_normal(
            [0] * 5, np.eye(5), size=5
        )  # Reduced size
    elif heatmap_type == "Checkerboard":
        data = np.indices((5, 5)).sum(axis=0) % 2  # Reduced size
    else:
        data = np.random.rand(5, 5)

    fig, ax = plt.subplots(figsize=(10, 8))
    set_plot_theme(fig, ax, theme)
    sns.heatmap(data, ax=ax, cmap="YlGnBu", annot=True, fmt=".2f")
    ax.set_title(f"{heatmap_type}")

    return ax

def create_custom_heatmap(df, var_x, var_y, var_value, colorscale, theme):
    """Create a heatmap from user data. If an invalid colorscale is given, fall back to a safe default."""
    if not var_x or not var_y or df is None:
        return None

    # Determine a valid colormap
    import matplotlib.pyplot as _plt
    if colorscale is None or (isinstance(colorscale, str) and (colorscale.startswith('#') or colorscale not in _plt.colormaps())):
        cmap_to_use = 'YlGnBu'
    else:
        cmap_to_use = colorscale

    fig, ax = plt.subplots(figsize=(10, 8))
    set_plot_theme(fig, ax, theme)

    # Build aggregation table
    if var_value:
        pivot_table = pd.pivot_table(df, values=var_value, index=var_y, columns=var_x, aggfunc='mean')
    else:
        pivot_table = pd.crosstab(df[var_y], df[var_x], normalize='all')

    sns.heatmap(pivot_table, ax=ax, cmap=cmap_to_use, annot=True, fmt=".2f")
    ax.set_title(f"Heatmap of {var_y} vs {var_x}")
    ax.set_xlabel(var_x.replace("_", " ").title())
    ax.set_ylabel(var_y.replace("_", " ").title())

    return ax