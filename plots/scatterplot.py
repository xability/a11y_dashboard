import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from plots.utils import set_plot_theme, color_palettes

def create_scatterplot(input_scatterplot_type, input_scatter_color, theme):
    """Create a scatter plot with regression layers based on input parameters"""
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
    
    # Ensure clean white background (remove any pink tinting)
    if theme != "Dark":
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
    
    # Layer 1: Scatter points (original layer)
    sns.scatterplot(x=x, y=y, ax=ax, color=color, s=60, alpha=0.7, label="Data Points")
    
    # Layer 2: Best fit straight line (linear regression)
    sns.regplot(x=x, y=y, ax=ax, scatter=False, color="red", 
                line_kws={'linewidth': 2, 'alpha': 0.8}, label="Linear Fit",
                ci=None)  # Remove confidence interval to avoid pink shading
    
    # Layer 3: Loess smooth line (LOWESS regression)
    sns.regplot(x=x, y=y, ax=ax, scatter=False, lowess=True, color="blue",
                line_kws={'linewidth': 2, 'alpha': 0.8, 'linestyle': '--'}, label="LOESS Smooth",
                ci=None)  # Remove confidence interval to avoid pink shading
    
    ax.set_title(f"{scatterplot_type}")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend()

    return ax

def create_custom_scatterplot(df, var_x, var_y, color, theme):
    """Create a scatter plot with regression layers from user data"""
    if not var_x or not var_y or df is None:
        return None
        
    fig, ax = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax, theme)
    
    # Ensure clean white background (remove any pink tinting)
    if theme != "Dark":
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
    
    # Layer 1: Scatter points (original layer)
    sns.scatterplot(data=df, x=var_x, y=var_y, color=color, ax=ax, 
                    s=60, alpha=0.7, label="Data Points")
    
    # Layer 2: Best fit straight line (linear regression)
    sns.regplot(data=df, x=var_x, y=var_y, ax=ax, scatter=False, color="red",
                line_kws={'linewidth': 2, 'alpha': 0.8}, label="Linear Fit",
                ci=None)  # Remove confidence interval to avoid pink shading
    
    # Layer 3: Loess smooth line (LOWESS regression)
    sns.regplot(data=df, x=var_x, y=var_y, ax=ax, scatter=False, lowess=True, color="blue",
                line_kws={'linewidth': 2, 'alpha': 0.8, 'linestyle': '--'}, label="LOESS Smooth",
                ci=None)  # Remove confidence interval to avoid pink shading
    
    ax.set_title(f"{var_y} vs {var_x}")
    ax.set_xlabel(var_x.replace("_", " ").title())
    ax.set_ylabel(var_y.replace("_", " ").title())
    ax.legend()
    
    return ax