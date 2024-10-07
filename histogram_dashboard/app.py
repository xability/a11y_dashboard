import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from shiny import App, ui, render, reactive
from maidr.widget.shiny import render_maidr

# Define color palettes
color_palettes = {
    "Default": "#007bc2",
    "Red": "#FF0000",
    "Green": "#00FF00",
    "Blue": "#0000FF",
    "Purple": "#800080",
    "Orange": "#FFA500"
}

# Define the UI components for the Shiny application with two tabs and theme selector
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
            )
        )
    ),
    ui.navset_tab(
        # First tab: Histogram Skewness
        ui.nav_panel(
            "Histogram Skewness",
            ui.input_select(
                "skewness_color",
                "Select histogram color:",
                choices=list(color_palettes.keys()),
                selected="Default"
            ),
            ui.output_ui("create_skewness_histogram"),
        ),
        # Second tab: Histogram Modality
        ui.nav_panel(
            "Histogram Modality",
            ui.input_select(
                "modality_color",
                "Select histogram color:",
                choices=list(color_palettes.keys()),
                selected="Default"
            ),
            ui.output_ui("create_modality_histogram"),
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
        skewness_type = random.choice(["Positive Skew", "Negative Skew", "Normal (No Skew)"])
        color = color_palettes[input.skewness_color()]

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
        ax.set_title("Histogram")  # Removed skewness type from the title
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")
        
        return ax

    # Modality Histogram
    @output
    @render_maidr
    def create_modality_histogram():
        modality_type = random.choice(["Unimodal", "Bimodal", "Multimodal"])
        color = color_palettes[input.modality_color()]

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
        ax.set_title("Histogram")  # Removed modality type from the title
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")
        
        return ax

# Create the app
app = App(app_ui, server)

# Run the app
if __name__ == "__main__":
    app.run()
