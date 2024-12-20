import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from shiny import App, ui, render, reactive
from maidr.widget.shiny import render_maidr
from scipy.stats import norm, beta

# Define color palettes
color_palettes = {
    "Default": "#007bc2",
    "Red": "#FF0000",
    "Green": "#00FF00",
    "Blue": "#0000FF",
    "Purple": "#800080",
    "Orange": "#FFA500"
}

# Define the UI components for the Shiny application with three tabs and theme selector
app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.style("""
            body.dark-theme { background-color: #2E2E2E; color: white; }
            body.light-theme { background-color: white; color: black; }
        """),
        ui.tags.script("""
            Shiny.addCustomMessageHandler("update_theme", function(theme) {
                document.body.classList.toggle("dark-theme", theme === "Dark");
                document.body.classList.toggle("light-theme", theme === "Light");
            });
        """)
    ),
    ui.row(
        ui.column(3,
            ui.input_select(
                "theme",
                "Theme:",
                choices=["Light", "Dark"],
                selected="Light"
            ),
            ui.input_select(
                "color",
                "Color:",
                choices=list(color_palettes.keys()),
                selected="Default"
            )
        )
    ),
    ui.navset_tab(
        # First tab: Histogram Skewness
        ui.nav_panel(
            "Histogram Skewness",
            ui.output_ui("create_skewness_histogram"),
        ),
        # Second tab: Histogram Modality
        ui.nav_panel(
            "Histogram Modality",
            ui.output_ui("create_modality_histogram"),
        ),
        # Third tab: Histogram Kurtosis
        ui.nav_panel(
            "Histogram Kurtosis",
            ui.output_ui("create_kurtosis_histogram"),
        ),
    )
)

# Define the server logic
def server(input, output, session):
    # Update the theme based on the selected option
    @reactive.Effect
    @reactive.event(input.theme)
    async def update_theme():
        await session.send_custom_message("update_theme", input.theme())

    # Helper function to set the theme
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

    # Skewness Histogram
    @output
    @render_maidr
    def create_skewness_histogram():
        skewness_types = ["Positive Skew", "Negative Skew", "Normal (No Skew)"]
        skewness_type = np.random.choice(skewness_types)
        color = color_palettes[input.color()]

        # Generate data based on the selected skewness
        if skewness_type == "Positive Skew":
            data = np.random.exponential(scale=2, size=1000)
        elif skewness_type == "Negative Skew":
            data = -np.random.exponential(scale=2, size=1000)
        else:  # Normal (No Skew)
            data = np.random.normal(size=1000)
        
        # Create the plot using matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        set_theme(fig, ax)
        sns.histplot(data, kde=True, bins=30, color=color, edgecolor="white", ax=ax)
        ax.set_title("Histogram")
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")
        
        return ax

    # Modality Histogram
    @output
    @render_maidr
    def create_modality_histogram():
        modality_types = ["Unimodal", "Bimodal", "Multimodal"]
        modality_type = np.random.choice(modality_types)
        color = color_palettes[input.color()]

        # Generate data based on the selected modality
        if modality_type == "Unimodal":
            data = np.random.normal(loc=0, scale=1, size=1000)
        elif modality_type == "Bimodal":
            data = np.concatenate([np.random.normal(-2, 0.5, size=500), np.random.normal(2, 0.5, size=500)])
        else:  # Multimodal
            data = np.concatenate([
                np.random.normal(-4, 0.5, size=300),
                np.random.normal(0, 0.5, size=400),
                np.random.normal(4, 0.5, size=300)
            ])
        
        # Create the plot using matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        set_theme(fig, ax)
        sns.histplot(data, kde=True, bins=30, color=color, edgecolor="white", ax=ax)
        ax.set_title("Histogram")
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")
        
        return ax

    # Kurtosis Histogram 
    @output
    @render_maidr
    def create_kurtosis_histogram():
        kurtosis_types = ["Leptokurtic", "Mesokurtic", "Platykurtic"]
        kurtosis_type = np.random.choice(kurtosis_types)
        color = color_palettes[input.color()]

        # Generate data and PDF based on the selected kurtosis
        x = np.linspace(-4, 4, 1000)
        bins = np.linspace(-4, 4, 40)  # Consistent bins for all histograms
        y_max = 0.9  # Increase y-axis maximum to accommodate the peak

        # Create the plot using matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))  # Create figure and axis BEFORE plotting

        # Set random seed for reproducibility
        np.random.seed(0)

        if kurtosis_type == "Leptokurtic":
            data = np.random.normal(0, 0.5, 1000) ** 3  # Leptokurtic distribution
            sns.histplot(data, bins=bins, kde=False, stat="density", ax=ax, color=color, edgecolor="black")
        elif kurtosis_type == "Mesokurtic":
            data = np.random.normal(size=10000)  # Normal distribution for Mesokurtic
            sns.histplot(data, bins=bins, kde=False, stat="density", ax=ax, color=color, edgecolor="black")
            # Generate and plot the PDF for the trend line
            pdf = norm.pdf(x)
            ax.plot(x, pdf, color=color, linewidth=2, label="PDF")
        else:  # Platykurtic
            data = beta.rvs(a=2, b=2, size=10000)  # Beta distribution for a flatter peak
            data = (data - 0.5) * 8  # Scale and center the data to match the range
            sns.histplot(data, bins=bins, kde=False, stat="density", ax=ax, color=color, edgecolor="black")
            # Generate and plot the PDF for the trend line
            pdf = beta.pdf((x / 8) + 0.5, a=2, b=2) / 8
            ax.plot(x, pdf, color=color, linewidth=2, label="PDF")

        # Set the titles and labels
        ax.set_title("Kurtosis Histogram")
        ax.set_xlabel("Value")
        ax.set_ylabel("Density")
        ax.set_xlim(-4, 4)
        ax.set_ylim(0, y_max)  # Adjust y-axis for better visualization

        set_theme(fig, ax)  # Assuming this is a custom function for styling

        return ax

# Create the app
app = App(app_ui, server)

# Run the app
if __name__ == "__main__":
    app.run()