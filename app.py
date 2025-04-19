import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from maidr.widget.shiny import render_maidr
from shiny import App, reactive, render, ui
from shiny.types import FileInfo

# Import plot modules
from plots.utils import color_palettes
from plots.histogram import create_histogram, create_custom_histogram
from plots.boxplot import create_boxplot, create_custom_boxplot
from plots.scatterplot import create_scatterplot, create_custom_scatterplot
from plots.barplot import create_barplot, create_custom_barplot
from plots.lineplot import create_lineplot, create_custom_lineplot
from plots.heatmap import create_heatmap, create_custom_heatmap
from plots.multilineplot import generate_multiline_data, create_multiline_plot, create_custom_multiline_plot

# Set random seed
np.random.seed(1000)

# Define the UI components for the Shiny application with tabs and sidebar
app_ui = ui.page_fluid(
    # Head content for custom CSS and JavaScript
    ui.head_content(
        ui.tags.style(
            """
            body.dark-theme { background-color: #2E2E2E; color: white; }
            body.light-theme { background-color: white; color: black; }
        """
        ),
        ui.tags.script(
            """
            Shiny.addCustomMessageHandler("update_theme", function(theme) {
                document.body.classList.toggle("dark-theme", theme === "Dark");
                document.body.classList.toggle("light-theme", theme === "Light");
            });
        """
        ),
    ),
    ui.navset_tab(
        ui.nav_menu(
            "Settings",
            ui.nav_control(
                ui.input_select(
                    "theme", "Theme:", choices=["Light", "Dark"], selected="Light"
                )
            ),
        ),
        # Fifth tab: Practice tab with file upload, data types, and custom plot creation
        ui.nav_panel(
            "Practice",
            ui.row(
                # Left column for file upload, table, and conditional dropdowns (50% width)
                ui.column(
                    6,
                    ui.input_file("file_upload", "Upload CSV File", accept=".csv"),
                    ui.output_table("data_types"),
                    ui.output_ui("plot_options"),  # Conditionally render dropdowns
                    ui.output_ui("variable_input"),  # Variable input for specific plot
                ),
                # Right column for the plot (50% width)
                ui.column(6, ui.output_ui("create_custom_plot")),
            ),
        ),
        # First tab: Histogram with dropdowns and plot
        ui.nav_panel(
            "Tutorial - Histogram",
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
                selected="Default",
            ),
            ui.output_ui("create_histogram_output"),
        ),
        # Second tab: Box Plot with a single variable for Tutorial
        ui.nav_panel(
            "Tutorial - Box Plot",
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
                selected="Default",
            ),
            ui.output_ui("create_boxplot_output"),
        ),
        # Third tab: Scatter Plot with dropdowns and plot
        ui.nav_panel(
            "Tutorial - Scatter Plot",
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
                selected="Default",
            ),
            ui.output_ui("create_scatterplot_output"),
        ),
        # Fourth tab: Bar Plot with dropdowns and plot
        ui.nav_panel(
            "Tutorial - Bar Plot",
            ui.input_select(
                "barplot_color",
                "Select bar plot color:",
                choices=list(color_palettes.keys()),
                selected="Default",
            ),
            ui.output_ui("create_barplot_output"),
        ),
        # New tab: Line Plot
        ui.nav_panel(
            "Tutorial - Line Plot",
            ui.input_select(
                "lineplot_type",
                "Select line plot type:",
                choices=[
                    "Linear Trend",
                    "Exponential Growth",
                    "Sinusoidal Pattern",
                    "Random Walk",
                ],
                selected="Linear Trend",
            ),
            ui.input_select(
                "lineplot_color",
                "Select line plot color:",
                choices=list(color_palettes.keys()),
                selected="Default",
            ),
            ui.output_ui("create_lineplot_output"),
        ),
        # New tab: Heatmap
        ui.nav_panel(
            "Tutorial - Heatmap",
            ui.input_select(
                "heatmap_type",
                "Select heatmap type:",
                choices=[
                    "Random",
                    "Correlated",
                    "Checkerboard",
                ],
                selected="Random",
            ),
            ui.output_ui("create_heatmap_output"),
        ),
        # New tab: Multiline Plot
        ui.nav_panel(
            "Tutorial - Multiline Plot",
            ui.input_select(
                "multiline_type",
                "Select multiline plot type:",
                choices=[
                    "Simple Trends",
                    "Seasonal Patterns",
                    "Growth Comparison",
                    "Random Series",
                ],
                selected="Simple Trends",
            ),
            ui.input_select(
                "multiline_color",
                "Select color palette:",
                choices=["Default", "Colorful", "Pastel", "Dark Tones", "Paired Colors", "Rainbow"],
                selected="Default",
            ),
            ui.output_ui("create_multiline_plot_output"),
        ),
        
    ),
)


# Define the server logic
def server(input, output, session):
    uploaded_data = reactive.Value(None)
    # Add a reactive value to store multiline plot data
    multiline_data = reactive.Value(None)

    # Update the theme based on the selected option
    @reactive.effect
    @reactive.event(input.theme)
    async def update_theme():
        await session.send_custom_message("update_theme", input.theme())

    # Tutorial - Histogram Plot
    @output
    @render_maidr
    def create_histogram_output():
        return create_histogram(input.distribution_type(), input.hist_color(), input.theme())

    # Tutorial - Box Plot
    @output
    @render_maidr
    def create_boxplot_output():
        return create_boxplot(input.boxplot_type(), input.boxplot_color(), input.theme())

    # Tutorial - Scatter Plot
    @output
    @render_maidr
    def create_scatterplot_output():
        return create_scatterplot(input.scatterplot_type(), input.scatter_color(), input.theme())

    # Tutorial - Bar Plot
    @output
    @render_maidr
    def create_barplot_output():
        return create_barplot(input.barplot_color(), input.theme())

    # Tutorial - Line Plot
    @output
    @render_maidr
    def create_lineplot_output():
        return create_lineplot(input.lineplot_type(), input.lineplot_color(), input.theme())

    # Tutorial - Heatmap
    @output
    @render_maidr
    def create_heatmap_output():
        return create_heatmap(input.heatmap_type(), input.theme())

    # Tutorial - Multiline Plot
    @reactive.Effect
    @reactive.event(input.multiline_type)
    def update_multiline_data():
        multiline_data.set(generate_multiline_data(input.multiline_type()))
    
    @output
    @render_maidr
    def create_multiline_plot_output():
        # Initialize data if it hasn't been done yet
        if multiline_data.get() is None:
            update_multiline_data()
        
        # Get the stored data and create the plot
        data = multiline_data.get()
        return create_multiline_plot(data, input.multiline_type(), input.multiline_color(), input.theme())

    # Practice Tab Logic
    @reactive.Effect
    @reactive.event(input.file_upload)
    def update_variable_choices():
        file: list[FileInfo] = input.file_upload()
        if file and len(file) > 0:
            df = pd.read_csv(file[0]["datapath"])
            uploaded_data.set(df)
            numeric_vars = df.select_dtypes(include=np.number).columns.tolist()
            categorical_vars = df.select_dtypes(include="object").columns.tolist()

            # Update dropdown choices for plots in Practice tab
            ui.update_select(
                "plot_type",
                choices=[
                    "",
                    "Histogram",
                    "Box Plot",
                    "Scatter Plot",
                    "Bar Plot",
                    "Line Plot",
                    "Heatmap",
                    "Multiline Plot",
                ],
            )
            ui.update_select("var_boxplot_x", choices=[""] + numeric_vars)
            ui.update_select("var_boxplot_y", choices=[""] + categorical_vars)

    @output
    @render.table
    def data_types():
        df = uploaded_data.get()
        if df is not None:
            data_summary = pd.DataFrame(
                {
                    "Variable": df.columns,
                    "Data Type": df.dtypes.astype(str).replace(
                        {
                            "object": "categorical",
                            "int64": "numeric",
                            "float64": "numeric",
                        }
                    ),
                }
            )
            return data_summary

    @output
    @render.ui
    def plot_options():
        df = uploaded_data.get()
        if df is not None:
            return ui.div(
                ui.input_select(
                    "plot_type",
                    "Select plot type:",
                    choices=[
                        "",
                        "Histogram",
                        "Box Plot",
                        "Scatter Plot",
                        "Bar Plot",
                        "Line Plot",
                        "Heatmap",
                        "Multiline Plot"
                    ],
                    selected="",
                ),
                ui.input_select(
                    "plot_color",
                    "Select plot color:",
                    choices=list(color_palettes.keys()),
                    selected="Default",
                ),
            )
        return ui.div()

    @output
    @render.ui
    def variable_input():
        df = uploaded_data.get()
        plot_type = input.plot_type()

        if df is not None and plot_type:
            numeric_vars = df.select_dtypes(include=np.number).columns.tolist()
            categorical_vars = df.select_dtypes(include="object").columns.tolist()
            all_vars = df.columns.tolist()

            if plot_type == "Histogram":
                return ui.input_select(
                    "var_histogram",
                    "Select variable for Histogram:",
                    choices=[""] + numeric_vars,
                )
            elif plot_type == "Box Plot":
                return ui.div(
                    ui.input_select(
                        "var_boxplot_x",
                        "Select numerical variable for X-axis:",
                        choices=[""] + numeric_vars,
                    ),
                    ui.input_select(
                        "var_boxplot_y",
                        "Select categorical variable for Y-axis (optional):",
                        choices=[""] + categorical_vars,
                        selected="",
                    ),
                )
            elif plot_type == "Scatter Plot":
                return ui.div(
                    ui.input_select(
                        "var_scatter_x",
                        "Select X variable:",
                        choices=[""] + numeric_vars,
                    ),
                    ui.output_ui("var_scatter_y_output"),
                )
            elif plot_type == "Bar Plot":
                return ui.input_select(
                    "var_bar_plot",
                    "Select variable for Bar Plot:",
                    choices=[""] + categorical_vars,
                )
            elif plot_type == "Line Plot":
                return ui.div(
                    ui.input_select(
                        "var_line_x", 
                        "Select X variable:", 
                        choices=[""] + numeric_vars
                    ),
                    ui.output_ui("var_line_y_output"),
                )
            elif plot_type == "Heatmap":
                return ui.div(
                    ui.input_select(
                        "var_heatmap_x", 
                        "Select X variable (categorical):", 
                        choices=[""] + categorical_vars
                    ),
                    ui.input_select(
                        "var_heatmap_y", 
                        "Select Y variable (categorical):", 
                        choices=[""] + categorical_vars
                    ),
                    ui.input_select(
                        "var_heatmap_value", 
                        "Select value variable (numeric):", 
                        choices=[""] + numeric_vars
                    ),
                    ui.input_select(
                        "heatmap_colorscale",
                        "Select color palette:",
                        choices=["YlOrRd", "viridis", "plasma", "inferno", "RdBu_r", "coolwarm"],
                        selected="YlOrRd",
                    )
                )
            elif plot_type == "Multiline Plot":
                return ui.div(
                    ui.input_select(
                        "var_multiline_x", 
                        "Select X variable (numeric):", 
                        choices=[""] + numeric_vars
                    ),
                    ui.output_ui("var_multiline_y_output"),
                    ui.input_select(
                        "var_multiline_group", 
                        "Select grouping variable (categorical):", 
                        choices=[""] + categorical_vars
                    ),
                    ui.input_select(
                        "multiline_palette",
                        "Select color palette:",
                        choices=["Default", "Colorful", "Pastel", "Dark Tones", "Paired Colors", "Rainbow"],
                        selected="Default",
                    )
                )
        return ui.div()

    # Dynamic Y variable selection for Scatter Plot
    @output
    @render.ui
    def var_scatter_y_output():
        df = uploaded_data.get()
        if df is not None:
            x_var = input.var_scatter_x()
            y_choices = [""] + [
                var
                for var in df.select_dtypes(include=np.number).columns
                if var != x_var
            ]
            return ui.input_select(
                "var_scatter_y", "Select Y variable:", choices=y_choices
            )
        return ui.div()

    # Dynamic Y variable selection for Line Plot
    @output
    @render.ui
    def var_line_y_output():
        df = uploaded_data.get()
        if df is not None:
            x_var = input.var_line_x()
            y_choices = [""] + [
                var
                for var in df.select_dtypes(include=np.number).columns
                if var != x_var
            ]
            return ui.input_select(
                "var_line_y", "Select Y variable:", choices=y_choices
            )
        return ui.div()

    # Dynamic Y variable selection for Multiline Plot
    @output
    @render.ui
    def var_multiline_y_output():
        df = uploaded_data.get()
        if df is not None:
            x_var = input.var_multiline_x()
            y_choices = [""] + [
                var
                for var in df.select_dtypes(include=np.number).columns
                if var != x_var
            ]
            return ui.input_select(
                "var_multiline_y", "Select Y variable:", choices=y_choices
            )
        return ui.div()

    @output
    @render_maidr
    def create_custom_plot():
        df = uploaded_data.get()
        plot_type = input.plot_type()
        color = color_palettes[input.plot_color()]
        theme = input.theme()

        if df is None or not plot_type:
            return None

        try:
            if plot_type == "Histogram":
                var = input.var_histogram()
                return create_custom_histogram(df, var, color, theme)
                
            elif plot_type == "Box Plot":
                var_x = input.var_boxplot_x()
                var_y = input.var_boxplot_y()
                return create_custom_boxplot(df, var_x, var_y, color, theme)
                
            elif plot_type == "Scatter Plot":
                var_x = input.var_scatter_x()
                var_y = input.var_scatter_y()
                return create_custom_scatterplot(df, var_x, var_y, color, theme)
                
            elif plot_type == "Bar Plot":
                var = input.var_bar_plot()
                return create_custom_barplot(df, var, color, theme)
                
            elif plot_type == "Line Plot":
                var_x = input.var_line_x()
                var_y = input.var_line_y()
                return create_custom_lineplot(df, var_x, var_y, color, theme)
                
            elif plot_type == "Heatmap":
                var_x = input.var_heatmap_x()
                var_y = input.var_heatmap_y()
                var_value = input.var_heatmap_value()
                colorscale = input.heatmap_colorscale()
                return create_custom_heatmap(df, var_x, var_y, var_value, colorscale, theme)
                
            elif plot_type == "Multiline Plot":
                var_x = input.var_multiline_x()
                var_y = input.var_multiline_y()
                var_group = input.var_multiline_group()
                palette = input.multiline_palette()
                return create_custom_multiline_plot(df, var_x, var_y, var_group, palette, theme)
                
            return None
        except Exception as e:
            print(f"Error generating plot: {str(e)}")
            return None


# Create the app
app = App(app_ui, server)

# Run the app
if __name__ == "__main__":
    app.run()
