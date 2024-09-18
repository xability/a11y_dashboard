import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from shiny import App, ui, render, reactive
from shiny.types import FileInfo
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
app_ui = ui.page_fluid(
    ui.navset_tab(
        ui.nav_menu(
            "Settings",
            ui.nav_control(
                ui.input_select(
                    "theme",
                    "Theme:",
                    choices=["Light", "Dark"],
                    selected="Light"
                )
            )
        ),

        # Fifth tab: Practice tab with file upload, data types, and custom plot creation
        ui.nav_panel(
            "Practice",
            ui.row(
                # Left column for file upload, table, and conditional dropdowns (50% width)
                ui.column(6,
                    ui.input_file("file_upload", "Upload CSV File", accept=".csv"),
                    ui.output_table("data_types"),
                    ui.output_ui("plot_options"),  # Conditionally render dropdowns
                    ui.output_ui("variable_input")  # Variable input for specific plot
                ),
                # Right column for the plot (50% width)
                ui.column(6,
                    ui.output_ui("create_custom_plot")
                )
            )
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
                selected="Default"
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
                selected="Default"
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
                selected="Default"
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
                selected="Default"
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
                selected="Default"
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
        )
    )
)

# Define the server logic
def server(input, output, session):
    uploaded_data = reactive.Value(None)

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

    @output
    @render.ui
    def plot_options():
        file = input.file_upload()  # Check if file is uploaded
        if file and len(file) > 0:  # Only show if file is present
            return ui.div(
                ui.input_select(
                    "plot_type",
                    "Select plot type:",
                    choices=["", "Histogram", "Box Plot", "Scatter Plot", "Bar Plot"],
                    selected=""
                ),
                ui.input_select(
                    "plot_color",
                    "Select plot color:",
                    choices=list(color_palettes.keys()),
                    selected="Default"
                )
            )
        return ui.div()  # Return an empty div if no file is uploaded

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
        ax.set_title(f"Box Plot: {boxplot_type}")
        ax.set_xlabel("Value")
        
        return ax

    # Tutorial - Scatter Plot
    @output
    @render_maidr
    def create_scatterplot():
        scatterplot_type = input.scatterplot_type()
        color = color_palettes[input.scatter_color()]

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

    # Tutorial - Bar Plot
    @output
    @render_maidr
    def create_barplot():
        color = color_palettes[input.barplot_color()]
        categories = ["Category A", "Category B", "Category C", "Category D", "Category E"]
        values = np.random.randint(10, 100, size=5)

        fig, ax = plt.subplots(figsize=(10, 6))
        set_theme(fig, ax)
        sns.barplot(x=categories, y=values, ax=ax, color=color)
        ax.set_title("Bar Plot of Categories")
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
        ax.set_title(f"Line Plot: {lineplot_type}")
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
            data = np.random.multivariate_normal([0] * 5, np.eye(5), size=5)  # Reduced size
        elif heatmap_type == "Checkerboard":
            data = np.indices((5, 5)).sum(axis=0) % 2  # Reduced size

        fig, ax = plt.subplots(figsize=(10, 8))
        set_theme(fig, ax)
        sns.heatmap(data, ax=ax, cmap="YlGnBu", annot=True, fmt=".2f")
        ax.set_title(f"Heatmap: {heatmap_type}")
        
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
            categorical_vars = df.select_dtypes(include='object').columns.tolist()
            
            # Update dropdown choices for plots in Practice tab
            ui.update_select("plot_type", choices=["", "Histogram", "Box Plot", "Scatter Plot", "Bar Plot", "Line Plot", "Heatmap"])
            ui.update_select("var_boxplot_x", choices=[""] + numeric_vars)
            ui.update_select("var_boxplot_y", choices=[""] + categorical_vars)

    @output
    @render.table
    def data_types():
        df = uploaded_data.get()
        if df is not None:
            data_summary = pd.DataFrame({
                'Variable': df.columns,
                'Data Type': df.dtypes.astype(str).replace(
                    {'object': 'categorical', 'int64': 'numeric', 'float64': 'numeric'})
            })
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
                    choices=["", "Histogram", "Box Plot", "Scatter Plot", "Bar Plot", "Line Plot", "Heatmap"],
                    selected=""
                ),
                ui.input_select(
                    "plot_color",
                    "Select plot color:",
                    choices=list(color_palettes.keys()),
                    selected="Default"
                )
            )
        return ui.div()

    @output
    @render.ui
    def variable_input():
        df = uploaded_data.get()
        plot_type = input.plot_type()

        if df is not None and plot_type:
            numeric_vars = df.select_dtypes(include=np.number).columns.tolist()
            categorical_vars = df.select_dtypes(include='object').columns.tolist()
            all_vars = df.columns.tolist()

            if plot_type == "Histogram":
                return ui.input_select("var_histogram", "Select variable for Histogram:", 
                                       choices=[""] + numeric_vars)
            elif plot_type == "Box Plot":
                return ui.div(
                    ui.input_select("var_boxplot_x", "Select numerical variable for X-axis:", choices=[""] + numeric_vars),
                    ui.input_select("var_boxplot_y", "Select categorical variable for Y-axis (optional):", choices=[""] + categorical_vars, selected="")
                )
            elif plot_type == "Scatter Plot":
                return ui.div(
                    ui.input_select("var_scatter_x", "Select X variable:", 
                                    choices=[""] + numeric_vars),
                    ui.output_ui("var_scatter_y_output")
                )
            elif plot_type == "Bar Plot":
                return ui.input_select("var_bar_plot", 
                                       "Select variable for Bar Plot:", 
                                       choices=[""] + categorical_vars)
            elif plot_type == "Line Plot":
                return ui.div(
                    ui.input_select("var_line_x", "Select X variable:", 
                                    choices=[""] + numeric_vars),
                    ui.output_ui("var_line_y_output")
                )
            elif plot_type == "Heatmap":
                return ui.div(
                    ui.input_select("var_heatmap_x", "Select X variable:", 
                                    choices=[""] + all_vars),
                    ui.output_ui("var_heatmap_y_output")
                )
        return ui.div()

    # Dynamic Y variable selection for Scatter Plot
    @output
    @render.ui
    def var_scatter_y_output():
        df = uploaded_data.get()
        if df is not None:
            x_var = input.var_scatter_x()
            y_choices = [""] + [var for var in df.select_dtypes(include=np.number).columns if var != x_var]
            return ui.input_select("var_scatter_y", "Select Y variable:", choices=y_choices)
        return ui.div()

    # Dynamic Y variable selection for Line Plot
    @output
    @render.ui
    def var_line_y_output():
        df = uploaded_data.get()
        if df is not None:
            x_var = input.var_line_x()
            y_choices = [""] + [var for var in df.select_dtypes(include=np.number).columns if var != x_var]
            return ui.input_select("var_line_y", "Select Y variable:", choices=y_choices)
        return ui.div()

    # Dynamic Y variable selection for Heatmap
    @output
    @render.ui
    def var_heatmap_y_output():
        df = uploaded_data.get()
        if df is not None:
            x_var = input.var_heatmap_x()
            y_choices = [""] + [var for var in df.columns if var != x_var]
            return ui.input_select("var_heatmap_y", "Select Y variable:", choices=y_choices)
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
                    ax.set_title(f"Histogram of {var}")
                    ax.set_xlabel(var.replace("_", " ").title())
                    ax.set_ylabel("Count")
            elif plot_type == "Box Plot":
                var_x = input.var_boxplot_x()
                var_y = input.var_boxplot_y()
                if var_x and var_y:
                    sns.boxplot(x=var_y, y=var_x, data=df, palette=[color], ax=ax)
                    ax.set_title(f"Box Plot of {var_x} grouped by {var_y}")
                    ax.set_xlabel(var_y.replace("_", " ").title())
                    ax.set_ylabel(var_x.replace("_", " ").title())
                elif var_x:
                    sns.boxplot(y=df[var_x], color=color, ax=ax)
                    ax.set_title(f"Box Plot of {var_x}")
                    ax.set_ylabel(var_x.replace("_", " ").title())
            elif plot_type == "Scatter Plot":
                var_x = input.var_scatter_x()
                var_y = input.var_scatter_y()
                if var_x and var_y:
                    sns.scatterplot(data=df, x=var_x, y=var_y, color=color, ax=ax)
                    ax.set_title(f"Scatter Plot: {var_y} vs {var_x}")
                    ax.set_xlabel(var_x.replace("_", " ").title())
                    ax.set_ylabel(var_y.replace("_", " ").title())
            elif plot_type == "Bar Plot":
                var = input.var_bar_plot()
                if var:
                    sns.countplot(data=df, x=var, color=color, ax=ax)
                    ax.set_title(f"Bar Plot of {var}")
                    ax.set_xlabel(var.replace("_", " ").title())
                    ax.set_ylabel("Count")
            elif plot_type == "Line Plot":
                var_x = input.var_line_x()
                var_y = input.var_line_y()
                if var_x and var_y:
                    sns.lineplot(data=df, x=var_x, y=var_y, color=color, ax=ax)
                    ax.set_title(f"Line Plot: {var_y} vs {var_x}")
                    ax.set_xlabel(var_x.replace("_", " ").title())
                    ax.set_ylabel(var_y.replace("_", " ").title())
            elif plot_type == "Heatmap":
                var_x = input.var_heatmap_x()
                var_y = input.var_heatmap_y()
                if var_x and var_y:
                    # Check if both variables are numerical
                    if df[var_x].dtype.kind in 'biufc' and df[var_y].dtype.kind in 'biufc':
                        pivot_table = df.pivot_table(values=var_y, columns=var_x, aggfunc='mean')
                    else:
                        # If at least one variable is categorical, use crosstab
                        pivot_table = pd.crosstab(df[var_y], df[var_x], normalize='all')
                    
                    sns.heatmap(pivot_table, ax=ax, cmap="YlGnBu", annot=True, fmt=".2f")
                    ax.set_title(f"Heatmap: {var_y} vs {var_x}")
                    ax.set_xlabel(var_x.replace("_", " ").title())
                    ax.set_ylabel(var_y.replace("_", " ").title())
                    
                    # # Rotate x-axis labels if there are many categories
                    # if len(pivot_table.columns) > 5:
                    #     plt.xticks(rotation=45, ha='right')

            return ax
        except Exception as e:
            print(f"Error generating plot: {str(e)}")
            return None

# Create the app
app = App(app_ui, server)

# Run the app
if __name__ == "__main__":
    app.run()