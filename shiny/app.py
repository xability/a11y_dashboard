import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from shiny import App, ui, render
from maidr.widget.shiny import render_maidr

# Set random seed
np.random.seed(1000)

# Define color palettes
color_palettes = {
    "Default": "#007bc2",
    "Red": "#FF0000",
    "Green": "#00FF00",
    "Blue": "#0000FF",
    "Purple": "#800080",
    "Orange": "#FFA500"
}

# Define the UI components for the Shiny application with tabs and sidebar
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons(
            "theme",
            "Select theme:",
            choices=["Light", "Dark"],
            selected="Light"
        ),
        width=2
    ),
    ui.navset_tab(
        # First tab: Histogram with dropdowns and plot
        ui.nav_panel(
            "Histogram",
            ui.input_select(
                "distribution_type",
                "Select histogram distribution type:",
                choices=[
                    "Normal Distribution",
                    "Positively Skewed",
                    "Negatively Skewed",
                    "Unimodal Distribution",
                    "Bimodal Distribution",
                    "Multimodal Distribution",
                ],
                selected="Normal Distribution",
            ),
            ui.input_select(
                "hist_color",
                "Select histogram color:",
                choices=list(color_palettes.keys()),
                selected="Default"
            ),
            ui.output_ui("create_histogram"),
        ),
        # Second tab: Box Plot with dropdowns and plot
        ui.nav_panel(
            "Box Plot",
            ui.input_select(
                "boxplot_type",
                "Select box plot type:",
                choices=[
                    "Positively Skewed with Outliers",
                    "Negatively Skewed with Outliers",
                    "Symmetric with Outliers",
                    "Symmetric without Outliers",
                ],
                selected="Positively Skewed with Outliers",
            ),
            ui.input_select(
                "boxplot_color",
                "Select box plot color:",
                choices=list(color_palettes.keys()),
                selected="Default"
            ),
            ui.output_ui("create_boxplot"),
        ),
        # Third tab: Scatter Plot with dropdowns and plot
        ui.nav_panel(
            "Scatter Plot",
            ui.input_select(
                "scatterplot_type",
                "Select scatter plot type:",
                choices=[
                    "No Correlation",
                    "Weak Positive Correlation",
                    "Strong Positive Correlation",
                    "Weak Negative Correlation",
                    "Strong Negative Correlation",
                ],
                selected="No Correlation",
            ),
            ui.input_select(
                "scatter_color",
                "Select scatter plot color:",
                choices=list(color_palettes.keys()),
                selected="Default"
            ),
            ui.output_ui("create_scatterplot"),
        )
    )
)

# Define the server logic for generating histograms, box plots, and scatter plots
def server(input, output, session):
    def set_theme(fig, ax):
        theme = input.theme()
        if theme == "Dark":
            plt.style.use('dark_background')
            fig.patch.set_facecolor('#2E2E2E')
            ax.set_facecolor('#2E2E2E')
        else:
            plt.style.use('default')
            fig.patch.set_facecolor('white')
            ax.set_facecolor('white')

    @render_maidr
    def create_histogram():
        distribution_type = input.distribution_type()
        color = color_palettes[input.hist_color()]

        # Generate data based on the selected distribution
        if distribution_type == "Normal Distribution":
            data = np.random.normal(size=1000)
        elif distribution_type == "Positively Skewed":
            data = np.random.exponential(scale=3, size=1000)
        elif distribution_type == "Negatively Skewed":
            data = -np.random.exponential(scale=1.5, size=1000)  # Modified to increase skew
        elif distribution_type == "Unimodal Distribution":
            data = np.random.normal(loc=0, scale=2.5, size=1000)
        elif distribution_type == "Bimodal Distribution":
            data = np.concatenate([np.random.normal(-2, 0.5, size=500), np.random.normal(2, 0.5, size=500)])
        elif distribution_type == "Multimodal Distribution":
            data = np.concatenate([np.random.normal(-2, 0.5, size=300), np.random.normal(2, 0.5, size=300), np.random.normal(5, 0.5, size=400)])
        else:
            data = np.random.normal(size=1000)
        
        # Create the plot using matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        set_theme(fig, ax)
        sns.histplot(data, kde=True, bins=20, color=color, edgecolor="white", ax=ax)
        ax.set_title(f"Histogram of {distribution_type}")
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")
        
        return ax  # Return the figure

    @render_maidr
    def create_boxplot():
        boxplot_type = input.boxplot_type()
        color = color_palettes[input.boxplot_color()]

        # Generate data based on the selected box plot type
        if boxplot_type == "Positively Skewed with Outliers":
            data = np.random.lognormal(mean=0, sigma=0.5, size=1000)
        elif boxplot_type == "Negatively Skewed with Outliers":
            data = -np.random.lognormal(mean=0, sigma=0.5, size=1000)  # More pronounced negative skew
        elif boxplot_type == "Symmetric with Outliers":
            data = np.random.normal(loc=0, scale=1, size=1000)
        elif boxplot_type == "Symmetric without Outliers":
            # Ensure no outliers by limiting range of data
            data = np.random.normal(loc=0, scale=1, size=1000)
            data = data[(data > -1.5) & (data < 1.5)]  # Strict range to avoid outliers
        else:
            data = np.random.normal(loc=0, scale=1, size=1000)

        # Calculate the IQR for outlier detection (only relevant for cases with outliers)
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        upper_bound = q3 + 1.5 * iqr
        lower_bound = q1 - 1.5 * iqr

        # Identify the outliers only for types that should have them
        if "Outliers" in boxplot_type:
            outliers = data[(data > upper_bound) | (data < lower_bound)]
            if len(outliers) > 5:
                outliers = outliers[:5]  # Limit to first 5 outliers
            data = np.clip(data, lower_bound, upper_bound)  # Cap the rest of the data
            data = np.concatenate([data, outliers])  # Add the outliers back into the dataset

        # Create the plot using matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        set_theme(fig, ax)
        sns.boxplot(x=data, ax=ax, color=color)
        ax.set_title(f"Box Plot: {boxplot_type}")
        ax.set_xlabel("Value")
        
        return ax

    @render_maidr
    def create_scatterplot():
        scatterplot_type = input.scatterplot_type()
        color = color_palettes[input.scatter_color()]

        # Generate data for scatter plot based on the selected correlation type
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

        # Create the plot using matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        set_theme(fig, ax)
        sns.scatterplot(x=x, y=y, ax=ax, color=color)
        ax.set_title(f"Scatter Plot: {scatterplot_type}")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        
        return ax

# Create the app
app = App(app_ui, server)

# Run the app
if __name__ == "__main__":
    app.run()