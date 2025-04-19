import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from maidr.widget.shiny import render_maidr
from shiny import App, reactive, render, ui
from shiny.types import FileInfo

# Set random seed
np.random.seed(1000)

# Define color palettes
color_palettes = {
    "Default": "#007bc2",
    "Red": "#FF0000",
    "Green": "#00FF00",
    "Blue": "#0000FF",
    "Purple": "#800080",
    "Orange": "#FFA500",
}

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
            ui.output_ui("create_histogram"),
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
            ui.output_ui("create_boxplot"),
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
            ui.output_ui("create_scatterplot"),
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
            ui.output_ui("create_barplot"),
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
            ui.output_ui("create_lineplot"),
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
            ui.output_ui("create_heatmap"),
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
            ui.output_ui("create_multiline_plot"),
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

    def set_theme(fig, ax):
        theme = input.theme()
        if theme == "Dark":
            plt.style.use("dark_background")
            fig.patch.set_facecolor("#2E2E2E")
            ax.set_facecolor("#2E2E2E")
        else:
            plt.style.use("default")
            fig.patch.set_facecolor("white")
            ax.set_facecolor("white")

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

    # Tutorial - Histogram Plot
    @output
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
            data = -np.random.exponential(scale=1.5, size=1000)
        elif distribution_type == "Unimodal Distribution":
            data = np.random.normal(loc=0, scale=2.5, size=1000)
        elif distribution_type == "Bimodal Distribution":
            data = np.concatenate(
                [
                    np.random.normal(-2, 0.5, size=500),
                    np.random.normal(2, 0.5, size=500),
                ]
            )
        elif distribution_type == "Multimodal Distribution":
            data = np.concatenate(
                [
                    np.random.normal(-2, 0.5, size=300),
                    np.random.normal(2, 0.5, size=300),
                    np.random.normal(5, 0.5, size=400),
                ]
            )
        else:
            data = np.random.normal(size=1000)

        # Create the plot using matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        set_theme(fig, ax)
        sns.histplot(data, kde=True, bins=20, color=color, edgecolor="white", ax=ax)
        ax.set_title(f"{distribution_type}")
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")

        return ax

    # Tutorial - Box Plot
    @output
    @render_maidr
    def create_boxplot():
        boxplot_type = input.boxplot_type()
        color = color_palettes[input.boxplot_color()]

        # Generate data based on the selected box plot type
        if boxplot_type == "Positively Skewed with Outliers":
            data = np.random.lognormal(mean=0, sigma=0.5, size=1000)
        elif boxplot_type == "Negatively Skewed with Outliers":
            data = -np.random.lognormal(mean=0, sigma=0.5, size=1000)
        elif boxplot_type == "Symmetric with Outliers":
            data = np.random.normal(loc=0, scale=1, size=1000)
        elif boxplot_type == "Symmetric without Outliers":
            data = np.random.normal(loc=0, scale=1, size=1000)
            data = data[(data > -1.5) & (data < 1.5)]  # Strict range to avoid outliers
        else:
            data = np.random.normal(loc=0, scale=1, size=1000)

        # Create the plot using matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        set_theme(fig, ax)
        sns.boxplot(x=data, ax=ax, color=color)  # Horizontal box plot
        ax.set_title(f"{boxplot_type}")
        ax.set_xlabel("Value")

        return ax

    # Tutorial - Scatter Plot
    @output
    @render_maidr
    def create_scatterplot():
        scatterplot_type = input.scatterplot_type()
        color = color_palettes[input.scatter_color()]

        num_points = np.random.randint(
            20, 31
        )  # Randomly select between 20 and 30 points
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
        ax.set_title(f"{scatterplot_type}")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        return ax

    # Tutorial - Bar Plot
    @output
    @render_maidr
    def create_barplot():
        color = color_palettes[input.barplot_color()]
        categories = [
            "Category A",
            "Category B",
            "Category C",
            "Category D",
            "Category E",
        ]
        values = np.random.randint(10, 100, size=5)

        fig, ax = plt.subplots(figsize=(10, 6))
        set_theme(fig, ax)
        sns.barplot(x=categories, y=values, ax=ax, color=color)
        ax.set_title("Plot of Categories")
        ax.set_xlabel("Categories")
        ax.set_ylabel("Values")

        return ax

    # Tutorial - Line Plot
    @output
    @render_maidr
    def create_lineplot():
        lineplot_type = input.lineplot_type()
        color = color_palettes[input.lineplot_color()]

        x = np.linspace(0, 10, 20)  # Reduced number of points
        if lineplot_type == "Linear Trend":
            y = 2 * x + 1 + np.random.normal(0, 1, 20)
        elif lineplot_type == "Exponential Growth":
            y = np.exp(0.5 * x) + np.random.normal(0, 1, 20)
        elif lineplot_type == "Sinusoidal Pattern":
            y = 5 * np.sin(x) + np.random.normal(0, 0.5, 20)
        elif lineplot_type == "Random Walk":
            y = np.cumsum(np.random.normal(0, 1, 20))

        fig, ax = plt.subplots(figsize=(10, 6))
        set_theme(fig, ax)
        sns.lineplot(x=x, y=y, ax=ax, color=color)
        ax.set_title(f"{lineplot_type}")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        return ax

    # New function: Tutorial - Heatmap
    @output
    @render_maidr
    def create_heatmap():
        heatmap_type = input.heatmap_type()

        if heatmap_type == "Random":
            data = np.random.rand(5, 5)  # Reduced size
        elif heatmap_type == "Correlated":
            data = np.random.multivariate_normal(
                [0] * 5, np.eye(5), size=5
            )  # Reduced size
        elif heatmap_type == "Checkerboard":
            data = np.indices((5, 5)).sum(axis=0) % 2  # Reduced size

        fig, ax = plt.subplots(figsize=(10, 8))
        set_theme(fig, ax)
        sns.heatmap(data, ax=ax, cmap="YlGnBu", annot=True, fmt=".2f")
        ax.set_title(f"{heatmap_type}")

        return ax

    # Tutorial - Multiline Plot
    @reactive.Effect
    @reactive.event(input.multiline_type)
    def update_multiline_data():
        multiline_type = input.multiline_type()
        
        # Generate different data based on the selected type
        x = np.linspace(0, 10, 30)  # 30 points for x-axis
        series_names = ["Series 1", "Series 2", "Series 3"]
        
        if multiline_type == "Simple Trends":
            # Linear trends with different slopes
            y1 = 1.5 * x + np.random.normal(0, 1, 30)
            y2 = 0.5 * x + 5 + np.random.normal(0, 1, 30)
            y3 = -x + 15 + np.random.normal(0, 1, 30)
        elif multiline_type == "Seasonal Patterns":
            # Sinusoidal patterns with different phases
            y1 = 5 * np.sin(x) + 10 + np.random.normal(0, 0.5, 30)
            y2 = 5 * np.sin(x + np.pi/2) + 10 + np.random.normal(0, 0.5, 30)
            y3 = 5 * np.sin(x + np.pi) + 10 + np.random.normal(0, 0.5, 30)
        elif multiline_type == "Growth Comparison":
            # Different growth patterns
            y1 = np.exp(0.2 * x) + np.random.normal(0, 0.5, 30)
            y2 = x**2 / 10 + np.random.normal(0, 1, 30)
            y3 = np.log(x + 1) * 5 + np.random.normal(0, 0.5, 30)
        else:  # Random Series
            # Random walks with different volatilities
            y1 = np.cumsum(np.random.normal(0, 0.5, 30))
            y2 = np.cumsum(np.random.normal(0.1, 0.7, 30))
            y3 = np.cumsum(np.random.normal(-0.05, 0.9, 30))
        
        # Store the data in a reactive value
        multiline_data.set(pd.DataFrame({
            "x": np.tile(x, 3),
            "y": np.concatenate([y1, y2, y3]),
            "series": np.repeat(series_names, len(x))
        }))
    
    @output
    @render_maidr
    def create_multiline_plot():
        # Only get the current palette, data comes from reactive value
        palette = input.multiline_color()
        multiline_type = input.multiline_type()
        
        # Initialize data if it hasn't been done yet
        if multiline_data.get() is None:
            update_multiline_data()
        
        # Get the stored data
        data = multiline_data.get()
        
        # Create the plot using matplotlib and seaborn
        fig, ax = plt.subplots(figsize=(10, 6))
        set_theme(fig, ax)
        
        # Map friendly palette names to seaborn palette names
        palette_mapping = {
            "Default": None,  # Use default seaborn palette
            "Colorful": "Set1",
            "Pastel": "Set2",
            "Dark Tones": "Dark2",
            "Paired Colors": "Paired",
            "Rainbow": "Spectral"
        }
        
        # Use seaborn lineplot for multiple lines
        if palette == "Default":
            # Use default seaborn color palette
            lineplot = sns.lineplot(
                x="x", y="y", hue="series", style="series", 
                markers=True, dashes=True, data=data, ax=ax
            )
        else:
            # Use selected color palette
            lineplot = sns.lineplot(
                x="x", y="y", hue="series", style="series", 
                markers=True, dashes=True, data=data, ax=ax,
                palette=palette_mapping[palette]
            )
        
        # Customize the plot
        ax.set_title(f"Multiline Plot: {multiline_type}")
        ax.set_xlabel("X values")
        ax.set_ylabel("Y values")
        
        return ax

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

    # Dynamic Y variable selection for Heatmap
    @output
    @render.ui
    def var_heatmap_y_output():
        df = uploaded_data.get()
        if df is not None:
            x_var = input.var_heatmap_x()
            y_choices = [""] + [var for var in df.columns if var != x_var]
            return ui.input_select(
                "var_heatmap_y", "Select Y variable:", choices=y_choices
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

        if df is None or not plot_type:
            return None

        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            set_theme(fig, ax)

            if plot_type == "Histogram":
                var = input.var_histogram()
                if var:
                    sns.histplot(data=df, x=var, kde=True, color=color, ax=ax)
                    ax.set_title(f"{var}")
                    ax.set_xlabel(var.replace("_", " ").title())
                    ax.set_ylabel("Count")
            elif plot_type == "Box Plot":
                var_x = input.var_boxplot_x()
                var_y = input.var_boxplot_y()
                if var_x and var_y:
                    sns.boxplot(x=var_y, y=var_x, data=df, palette=[color], ax=ax)
                    ax.set_title(f"{var_x} grouped by {var_y}")
                    ax.set_xlabel(var_y.replace("_", " ").title())
                    ax.set_ylabel(var_x.replace("_", " ").title())
                elif var_x:
                    sns.boxplot(y=df[var_x], color=color, ax=ax)
                    ax.set_title(f"{var_x}")
                    ax.set_ylabel(var_x.replace("_", " ").title())
            elif plot_type == "Scatter Plot":
                var_x = input.var_scatter_x()
                var_y = input.var_scatter_y()
                if var_x and var_y:
                    sns.scatterplot(data=df, x=var_x, y=var_y, color=color, ax=ax)
                    ax.set_title(f"{var_y} vs {var_x}")
                    ax.set_xlabel(var_x.replace("_", " ").title())
                    ax.set_ylabel(var_y.replace("_", " ").title())
            elif plot_type == "Bar Plot":
                var = input.var_bar_plot()
                if var:
                    sns.countplot(data=df, x=var, color=color, ax=ax)
                    ax.set_title(f"{var}")
                    ax.set_xlabel(var.replace("_", " ").title())
                    ax.set_ylabel("Count")
            elif plot_type == "Line Plot":
                var_x = input.var_line_x()
                var_y = input.var_line_y()
                if var_x and var_y:
                    sns.lineplot(data=df, x=var_x, y=var_y, color=color, ax=ax)
                    ax.set_title(f"{var_y} vs {var_x}")
                    ax.set_xlabel(var_x.replace("_", " ").title())
                    ax.set_ylabel(var_y.replace("_", " ").title())
            elif plot_type == "Heatmap":
                var_x = input.var_heatmap_x()
                var_y = input.var_heatmap_y()
                if var_x and var_y:
                    # Check if both variables are numerical
                    if (
                        df[var_x].dtype.kind in "biufc"
                        and df[var_y].dtype.kind in "biufc"
                    ):
                        pivot_table = df.pivot_table(
                            values=var_y, columns=var_x, aggfunc="mean"
                        )
                    else:
                        # If at least one variable is categorical, use crosstab
                        pivot_table = pd.crosstab(df[var_y], df[var_x], normalize="all")

                    sns.heatmap(
                        pivot_table, ax=ax, cmap="YlGnBu", annot=True, fmt=".2f"
                    )
                    ax.set_title(f"{var_y} vs {var_x}")
                    ax.set_xlabel(var_x.replace("_", " ").title())
                    ax.set_ylabel(var_y.replace("_", " ").title())
            elif plot_type == "Multiline Plot":
                var_x = input.var_multiline_x()
                var_y = input.var_multiline_y()
                var_group = input.var_multiline_group()
                palette = input.multiline_palette()
                
                if var_x and var_y and var_group:
                    # Map friendly palette names to seaborn palette names
                    palette_mapping = {
                        "Default": None,  # Use default seaborn palette
                        "Colorful": "Set1",
                        "Pastel": "Set2",
                        "Dark Tones": "Dark2",
                        "Paired Colors": "Paired",
                        "Rainbow": "Spectral"
                    }
                    
                    # Use seaborn lineplot for multiple lines
                    if palette == "Default":
                        # Use default seaborn color palette
                        lineplot = sns.lineplot(
                            x=var_x, y=var_y, hue=var_group, style=var_group, 
                            markers=True, dashes=True, data=df, ax=ax
                        )
                    else:
                        # Use selected color palette
                        lineplot = sns.lineplot(
                            x=var_x, y=var_y, hue=var_group, style=var_group, 
                            markers=True, dashes=True, data=df, ax=ax,
                            palette=palette_mapping[palette]
                        )
                    
                    # Customize the plot
                    ax.set_title(f"{var_y} vs {var_x} by {var_group}")
                    ax.set_xlabel(var_x.replace("_", " ").title())
                    ax.set_ylabel(var_y.replace("_", " ").title())
                    
                    # Import maidr for accessibility
                    import maidr
            return ax
        except Exception as e:
            print(f"Error generating plot: {str(e)}")
            return None


# Create the app
app = App(app_ui, server)

# Run the app
if __name__ == "__main__":
    app.run()
