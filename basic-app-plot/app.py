import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from shiny import App, ui
from maidr.widget.shiny import render_maidr

# Set random seed
np.random.seed(1000)

# Define the UI components for the Shiny application
app_ui = ui.page_fluid(
    ui.row(
        ui.column(
            3,
            ui.input_select(
                "distribution_type",
                "Select distribution type:",
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
        ),
        ui.column(9, ui.output_ui("create_histogram")),
    )
)

# Define the server logic for generating histograms based on the distribution type
def server(inp, _, __):
    @render_maidr
    def create_histogram():
        distribution_type = inp.distribution_type()

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
        
        # Create the plot using seaborn
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(data, kde=True, color="#007bc2", edgecolor="white", ax=ax)
        ax.set_title(f"Histogram of {distribution_type}")
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")
        
        return ax

# Create the app
app = App(app_ui, server)

# Run the app
if __name__ == "__main__":
    app.run()
