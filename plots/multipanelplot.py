import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from plots.utils import set_plot_theme

def generate_multipanel_data():
    """Generate sample data for the multipanel plot"""
    # Data for line plot
    x_line = np.array([1, 2, 3, 4, 5, 6, 7, 8])
    y_line = np.array([2, 4, 1, 5, 3, 7, 6, 8])
    
    # Data for first bar plot
    categories = ["A", "B", "C", "D", "E"]
    values = np.random.rand(5) * 10
    
    # Data for second bar plot
    categories_2 = ["A", "B", "C", "D", "E"]
    values_2 = np.random.randn(5) * 100
    
    # Data for scatter plot
    x_scatter = np.random.randn(50)
    y_scatter = np.random.randn(50)
    
    # Create a dictionary with the generated data
    return {
        "x_line": x_line,
        "y_line": y_line,
        "categories": categories,
        "values": values,
        "categories_2": categories_2,
        "values_2": values_2,
        "x_scatter": x_scatter,
        "y_scatter": y_scatter
    }

def create_multipanel_plot(layout_type, color_palette, theme):
    """
    Create a multipanel plot with different subplot types arranged in a specified layout.
    
    Parameters
    ----------
    layout_type : str
        The type of layout ('Grid 2x2', 'Row', 'Column', 'Mixed')
    color_palette : str
        The color palette to use for the plots
    theme : str
        The theme to apply to the plot ('Light' or 'Dark')
        
    Returns
    -------
    plt.Axes
        The first axes object of the created plot (for maidr compatibility).
    """
    # Generate sample data
    data = generate_multipanel_data()
    x_line = data["x_line"]
    y_line = data["y_line"]
    categories = data["categories"]
    values = data["values"]
    categories_2 = data["categories_2"]
    values_2 = data["values_2"]
    x_scatter = data["x_scatter"]
    y_scatter = data["y_scatter"]
    
    # Create a figure with 3 subplots arranged vertically
    fig, axs = plt.subplots(3, 1, figsize=(10, 12))
    
    # First panel: Line plot
    axs[0].plot(x_line, y_line, color="blue", linewidth=2)
    axs[0].set_title("Line Plot: Random Data")
    axs[0].set_xlabel("X-axis")
    axs[0].set_ylabel("Values")
    axs[0].grid(True, linestyle="--", alpha=0.7)
    
    # Second panel: Bar plot
    axs[1].bar(categories, values, color="green", alpha=0.7)
    axs[1].set_title("Bar Plot: Random Values")
    axs[1].set_xlabel("Categories")
    axs[1].set_ylabel("Values")
    
    # Third panel: Bar plot
    axs[2].bar(categories_2, values_2, color="blue", alpha=0.7)
    axs[2].set_title("Bar Plot 2: Random Values")
    axs[2].set_xlabel("Categories")
    axs[2].set_ylabel("Values")
    
    # Apply theme to all subplots
    for ax in axs.flat:
        set_plot_theme(fig, ax, theme)
    
    # Adjust layout to prevent overlap
    plt.tight_layout()
    
    # Return the first axes object for maidr compatibility
    return axs[0]

def create_custom_multipanel_plot(df, vars_config, layout_type, color_palette, theme):
    """
    Create a custom multipanel plot from user data.
    
    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe containing the data to plot
    vars_config : dict
        Dictionary containing variables for each subplot
        Example: {
            'plot1': {'type': 'line', 'x': 'col1', 'y': 'col2'},
            'plot2': {'type': 'bar', 'x': 'col3', 'y': 'col4'},
            'plot3': {'type': 'bar', 'x': 'col5', 'y': 'col6'},
        }
    layout_type : str
        The type of layout ('Vertical', 'Horizontal', 'Grid')
    color_palette : str
        The color palette to use for the plots
    theme : str
        The theme to apply to the plot ('Light' or 'Dark')
        
    Returns
    -------
    plt.Axes
        The first axes object of the created plot (for maidr compatibility).
    """
    if df is None or not vars_config:
        return None
    
    # Extract configuration for each plot
    plot1_config = vars_config.get('plot1', {})
    plot2_config = vars_config.get('plot2', {})
    plot3_config = vars_config.get('plot3', {})
    
    plot1_type = plot1_config.get('type', 'line')
    plot1_x = plot1_config.get('x', None)
    plot1_y = plot1_config.get('y', None)
    
    plot2_type = plot2_config.get('type', 'bar')
    plot2_x = plot2_config.get('x', None)
    plot2_y = plot2_config.get('y', None)
    
    plot3_type = plot3_config.get('type', 'bar')
    plot3_x = plot3_config.get('x', None)
    plot3_y = plot3_config.get('y', None)
    
    # Check if required variables exist
    if not all([plot1_x, plot1_y, plot2_x, plot2_y, plot3_x, plot3_y]):
        return None
    
    if not all([var in df.columns for var in [plot1_x, plot1_y, plot2_x, plot2_y, plot3_x, plot3_y]]):
        return None
    
    # Create the figure with 3 subplots arranged vertically
    fig, axs = plt.subplots(3, 1, figsize=(10, 12))
    
    # First panel
    if plot1_type == 'line':
        axs[0].plot(df[plot1_x], df[plot1_y], color="blue", linewidth=2)
        axs[0].set_title(f"Line Plot: {plot1_y} vs {plot1_x}")
        axs[0].grid(True, linestyle="--", alpha=0.7)
    elif plot1_type == 'scatter':
        axs[0].scatter(df[plot1_x], df[plot1_y], color="blue", alpha=0.7)
        axs[0].set_title(f"Scatter Plot: {plot1_y} vs {plot1_x}")
    elif plot1_type == 'bar':
        if df[plot1_x].dtype == 'object' or df[plot1_x].nunique() < 15:
            # For categorical x or small number of values
            value_counts = df.groupby(plot1_x)[plot1_y].mean()
            value_counts.plot(kind='bar', ax=axs[0], color="blue", alpha=0.7)
        else:
            axs[0].bar(df[plot1_x], df[plot1_y], color="blue", alpha=0.7)
        axs[0].set_title(f"Bar Plot: {plot1_y} by {plot1_x}")
    
    axs[0].set_xlabel(plot1_x.replace("_", " ").title())
    axs[0].set_ylabel(plot1_y.replace("_", " ").title())
    
    # Second panel
    if plot2_type == 'line':
        axs[1].plot(df[plot2_x], df[plot2_y], color="green", linewidth=2)
        axs[1].set_title(f"Line Plot: {plot2_y} vs {plot2_x}")
        axs[1].grid(True, linestyle="--", alpha=0.7)
    elif plot2_type == 'scatter':
        axs[1].scatter(df[plot2_x], df[plot2_y], color="green", alpha=0.7)
        axs[1].set_title(f"Scatter Plot: {plot2_y} vs {plot2_x}")
    elif plot2_type == 'bar':
        if df[plot2_x].dtype == 'object' or df[plot2_x].nunique() < 15:
            # For categorical x or small number of values
            value_counts = df.groupby(plot2_x)[plot2_y].mean()
            value_counts.plot(kind='bar', ax=axs[1], color="green", alpha=0.7)
        else:
            axs[1].bar(df[plot2_x], df[plot2_y], color="green", alpha=0.7)
        axs[1].set_title(f"Bar Plot: {plot2_y} by {plot2_x}")
    
    axs[1].set_xlabel(plot2_x.replace("_", " ").title())
    axs[1].set_ylabel(plot2_y.replace("_", " ").title())
    
    # Third panel
    if plot3_type == 'line':
        axs[2].plot(df[plot3_x], df[plot3_y], color="blue", linewidth=2)
        axs[2].set_title(f"Line Plot: {plot3_y} vs {plot3_x}")
        axs[2].grid(True, linestyle="--", alpha=0.7)
    elif plot3_type == 'scatter':
        axs[2].scatter(df[plot3_x], df[plot3_y], color="blue", alpha=0.7)
        axs[2].set_title(f"Scatter Plot: {plot3_y} vs {plot3_x}")
    elif plot3_type == 'bar':
        if df[plot3_x].dtype == 'object' or df[plot3_x].nunique() < 15:
            # For categorical x or small number of values
            value_counts = df.groupby(plot3_x)[plot3_y].mean()
            value_counts.plot(kind='bar', ax=axs[2], color="blue", alpha=0.7)
        else:
            axs[2].bar(df[plot3_x], df[plot3_y], color="blue", alpha=0.7)
        axs[2].set_title(f"Bar Plot: {plot3_y} by {plot3_x}")
    
    axs[2].set_xlabel(plot3_x.replace("_", " ").title())
    axs[2].set_ylabel(plot3_y.replace("_", " ").title())
    
    # Apply theme to all subplots
    for ax in axs.flat:
        set_plot_theme(fig, ax, theme)
    
    # Adjust layout to prevent overlap
    plt.tight_layout()
    
    # Return the first axes object for maidr compatibility
    return axs[0]