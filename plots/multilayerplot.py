import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from plots.utils import set_plot_theme, color_palettes

def generate_multilayer_data():
    """Generate sample data for the multilayer plot"""
    x = np.arange(8)
    bar_data = np.array([3, 5, 2, 7, 3, 6, 4, 5])
    hist_data = np.concatenate([np.random.normal(loc=i, scale=0.5, size=20) for i in x])
    scatter_data = np.array([4, 6, 3, 8, 2, 7, 5, 6])
    line_data = np.array([10, 8, 12, 14, 9, 11, 13, 10])
    
    # Create a dictionary with the generated data
    return {
        "x": x,
        "bar_data": bar_data,
        "hist_data": hist_data,
        "scatter_data": scatter_data,
        "line_data": line_data
    }

def create_multilayer_plot(input_background_type, background_color, line_color, theme):
    """
    Create a multilayer plot with a selected background plot type and a line chart in the foreground.
    
    Parameters
    ----------
    input_background_type : str
        The type of background plot ('Bar Plot', 'Histogram', or 'Scatter Plot')
    background_color : str
        The color to use for the background plot
    line_color : str
        The color to use for the line plot
    theme : str
        The theme to apply to the plot ('Light' or 'Dark')
        
    Returns
    -------
    plt.Axes
        The axes object of the created plot.
    """
    # Generate sample data
    data = generate_multilayer_data()
    x = data["x"]
    bar_data = data["bar_data"]
    hist_data = data["hist_data"]
    scatter_data = data["scatter_data"]
    line_data = data["line_data"]
    
    # Create a figure and a set of subplots
    fig, ax1 = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax1, theme)
    
    # Get colors from the color_palettes dictionary or use default if not found
    bg_color = color_palettes.get(background_color, "skyblue")
    ln_color = color_palettes.get(line_color, "red")
    
    # Create the background plot based on the selected type
    if input_background_type == "Bar Plot":
        ax1.bar(x, bar_data, color=bg_color, label="Bar Data", alpha=0.7)
        ax1.set_ylabel("Bar Values", color=bg_color)
        y_min, y_max = 0, max(bar_data) * 1.2
    
    elif input_background_type == "Histogram":
        # For histogram, we need to adjust the scale to fit with line plot
        bins = np.linspace(min(hist_data), max(hist_data), 20)
        ax1.hist(hist_data, bins=bins, color=bg_color, label="Histogram Data", alpha=0.7)
        ax1.set_ylabel("Frequency", color=bg_color)
        y_min, y_max = 0, ax1.get_ylim()[1] * 1.2
    
    elif input_background_type == "Scatter Plot":
        ax1.scatter(x, scatter_data, color=bg_color, label="Scatter Data", alpha=0.7, s=100)
        ax1.set_ylabel("Y Values", color=bg_color)
        y_min, y_max = min(scatter_data) * 0.8, max(scatter_data) * 1.2
    
    ax1.tick_params(axis="y", labelcolor=bg_color)
    ax1.set_xlabel("X Values")
    
    # Set y-axis limits for the background plot
    ax1.set_ylim(y_min, y_max)
    
    # Create a second y-axis sharing the same x-axis
    ax2 = ax1.twinx()
    
    # Create the line chart on the second y-axis
    ax2.plot(x, line_data, color=ln_color, marker="o", linestyle="-", linewidth=2, label="Line Data")
    ax2.set_ylabel("Line Values", color=ln_color)
    ax2.tick_params(axis="y", labelcolor=ln_color)
    
    # Add title
    ax1.set_title(f"Multilayer Plot: {input_background_type} with Line Plot")
    
    # Add legends for both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    
    # Adjust layout
    fig.tight_layout()
    
    return ax1

def create_custom_multilayer_plot(df, var_x, var_background, var_line, background_type, background_color, line_color, theme):
    """
    Create a custom multilayer plot from user data.
    
    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe containing the data to plot
    var_x : str
        The name of the column to use for the x-axis
    var_background : str
        The name of the column to use for the background plot
    var_line : str
        The name of the column to use for the line chart
    background_type : str
        The type of background plot ('Bar Plot', 'Histogram', or 'Scatter Plot')
    background_color : str
        The color to use for the background plot
    line_color : str
        The color to use for the line plot
    theme : str
        The theme to apply to the plot ('Light' or 'Dark')
        
    Returns
    -------
    plt.Axes
        The axes object of the created plot.
    """
    if not var_x or not var_background or not var_line or df is None:
        return None
    
    # Create a figure and a set of subplots
    fig, ax1 = plt.subplots(figsize=(10, 6))
    set_plot_theme(fig, ax1, theme)
    
    # Get data from dataframe
    x = df[var_x].values
    background_data = df[var_background].values
    line_data = df[var_line].values
    
    # Get colors from the color_palettes dictionary or use default if not found
    bg_color = color_palettes.get(background_color, "skyblue")
    ln_color = color_palettes.get(line_color, "red")
    
    # Create the background plot based on the selected type
    if background_type == "Bar Plot":
        # For categorical x, we may need to handle the x-axis differently
        if df[var_x].dtype == 'object':
            x_positions = np.arange(len(x))
            ax1.bar(x_positions, background_data, color=bg_color, label=var_background, alpha=0.7)
            ax1.set_xticks(x_positions)
            ax1.set_xticklabels(x)
        else:
            ax1.bar(x, background_data, color=bg_color, label=var_background, alpha=0.7)
        
        ax1.set_ylabel(var_background.replace("_", " ").title(), color=bg_color)
        y_min, y_max = 0, max(background_data) * 1.2
    
    elif background_type == "Histogram":
        # For histogram, we just use the background data column
        bins = np.linspace(min(background_data), max(background_data), 20)
        ax1.hist(background_data, bins=bins, color=bg_color, label=var_background, alpha=0.7)
        ax1.set_ylabel("Frequency", color=bg_color)
        y_min, y_max = 0, ax1.get_ylim()[1] * 1.2
    
    elif background_type == "Scatter Plot":
        # For categorical x, we may need to handle the x-axis differently
        if df[var_x].dtype == 'object':
            x_positions = np.arange(len(x))
            ax1.scatter(x_positions, background_data, color=bg_color, label=var_background, alpha=0.7, s=100)
            ax1.set_xticks(x_positions)
            ax1.set_xticklabels(x)
        else:
            ax1.scatter(x, background_data, color=bg_color, label=var_background, alpha=0.7, s=100)
            
        ax1.set_ylabel(var_background.replace("_", " ").title(), color=bg_color)
        y_min, y_max = min(background_data) * 0.8, max(background_data) * 1.2
    
    ax1.tick_params(axis="y", labelcolor=bg_color)
    ax1.set_xlabel(var_x.replace("_", " ").title())
    
    # Set y-axis limits for the background plot
    ax1.set_ylim(y_min, y_max)
    
    # Create a second y-axis sharing the same x-axis
    ax2 = ax1.twinx()
    
    # Create the line chart on the second y-axis
    # For categorical x, we may need to handle the x-axis differently
    if df[var_x].dtype == 'object' and background_type != "Histogram":
        x_positions = np.arange(len(x))
        ax2.plot(x_positions, line_data, color=ln_color, marker="o", linestyle="-", linewidth=2, label=var_line)
    else:
        ax2.plot(x, line_data, color=ln_color, marker="o", linestyle="-", linewidth=2, label=var_line)
        
    ax2.set_ylabel(var_line.replace("_", " ").title(), color=ln_color)
    ax2.tick_params(axis="y", labelcolor=ln_color)
    
    # Add title
    ax1.set_title(f"{var_background} ({background_type}) and {var_line} vs {var_x}")
    
    # Add legends for both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    
    # Adjust layout
    fig.tight_layout()
    
    return ax1