import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from shiny import App, ui, render
from maidr.widget.shiny import render_maidr

# Set random seed
np.random.seed(1000)

# Define the UI components for the Shiny application with tabs
app_ui = ui.page_fluid(
    ui.navset_tab(
        # First tab: Histogram with dropdown and plot
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
            ui.output_ui("create_histogram"),
        ),
        # Second tab: Box Plot with dropdown and plot
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
            ui.output_ui("create_boxplot"),
        ),
        # Third tab: Scatter Plot with dropdown and plot
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
            ui.output_ui("create_scatterplot"),
        )
    )
)

# Define the server logic for generating histograms, box plots, and scatter plots
def server(input, output, session):
    @render_maidr
    def create_histogram():
        distribution_type = input.distribution_type()

        # Generate data based on the selected distribution
        if distribution_type == "Normal Distribution":
            data = np.random.normal(size=1000)
        elif distribution_type == "Positively Skewed":
            data = np.random.exponential(scale=3, size=1000)
        elif distribution_type == "Negatively Skewed":
            data = -np.random.exponential(scale=2, size=1000) + 5
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
        hist_plot = sns.histplot(data, kde=True, bins=20, color="#007bc2", edgecolor="white", ax=ax)
        ax.set_title(f"Histogram of {distribution_type}")
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")
        
        return hist_plot

    @render_maidr
    def create_boxplot():
        boxplot_type = input.boxplot_type()

        # Generate data based on the selected box plot type
        if boxplot_type == "Positively Skewed with Outliers":
            data = np.random.lognormal(mean=0, sigma=0.5, size=1000)
        elif boxplot_type == "Negatively Skewed":
            data = -np.random.lognormal(mean=0, sigma=0.5, size=1000)
        elif boxplot_type == "Symmetric with Outlier":
            data = np.random.normal(loc=0, scale=1, size=1000)
        elif boxplot_type == "Symmetric without Outlier":
            data = np.random.normal(loc=0, scale=1, size=1000)
            data = data[np.abs(data) < 2]  # Remove extreme values that might be outliers
        else:
            data = np.random.normal(loc=0, scale=1, size=1000)

        # Calculate the IQR
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        upper_bound = q3 + 1.5 * iqr
        lower_bound = q1 - 1.5 * iqr

        # Identify the outliers
        outliers = data[(data > upper_bound) | (data < lower_bound)]
        
        # If there are more than 5 outliers, keep only the first 5
        if len(outliers) > 5:
            outliers = outliers[:5]
        
        # All other data points that are outliers beyond 5 are capped to be within bounds
        data[(data > upper_bound)] = upper_bound
        data[(data < lower_bound)] = lower_bound
        
        # Add the 5 outliers back into the dataset
        data = np.concatenate([data, outliers])

        # Create the plot using matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(x=data, ax=ax, color="#007bc2")
        ax.set_title(f"Box Plot: {boxplot_type}")
        ax.set_xlabel("Value")
        
        return ax

    @render_maidr
    def create_scatterplot():
        scatterplot_type = input.scatterplot_type()

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
        scatter_plot = sns.scatterplot(x=x, y=y, ax=ax)
        ax.set_title(f"Scatter Plot: {scatterplot_type}")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        
        return scatter_plot

# Create the app
app = App(app_ui, server)

# Run the app
if __name__ == "__main__":
    app.run()