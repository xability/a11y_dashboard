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
                    "Negatively Skewed",
                    "Symmetric with Outlier",
                    "Symmetric without Outlier",
                ],
                selected="Positively Skewed with Outliers",
            ),
            ui.output_ui("create_boxplot"),
        )
    )
)

# Define the server logic for generating histograms and box plots
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
            outliers = np.random.uniform(low=np.max(data), high=np.max(data)*1.5, size=5)
            data = np.concatenate([data, outliers])
        elif boxplot_type == "Negatively Skewed":
            data = -np.random.lognormal(mean=0, sigma=0.5, size=1000)
        elif boxplot_type == "Symmetric with Outlier":
            # Generate symmetric data
            data = np.random.normal(loc=0, scale=1, size=1000)
            # Add outliers symmetrically
            high_outliers = np.random.uniform(low=3, high=4, size=3)
            low_outliers = np.random.uniform(low=-4, high=-3, size=3)
            data = np.concatenate([data, high_outliers, low_outliers])
        elif boxplot_type == "Symmetric without Outlier":
            data = np.random.normal(loc=0, scale=1, size=1000)
            # Limit the range of data to ensure no outliers
            data = data[np.abs(data) < 2]  # Remove extreme values that might be outliers
        else:
            data = np.random.normal(loc=0, scale=1, size=1000)

        # Create the plot using matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        box_plot = sns.boxplot(x=data, ax=ax, color="#007bc2")
        ax.set_title(f"Box Plot: {boxplot_type}")
        ax.set_xlabel("Value")
        
        return box_plot

# Create the app
app = App(app_ui, server)

# Run the app
if __name__ == "__main__":
    app.run()