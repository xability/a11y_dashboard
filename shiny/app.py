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
            ui.input_file("file_upload", "Upload CSV File", accept=".csv"),
            ui.output_table("data_types"),
            ui.output_ui("plot_options"),
            ui.output_ui("variable_input"),
            ui.output_ui("create_custom_plot")
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
        )
    )
)

# Define the server logic for generating histograms, box plots, scatter plots, bar plots, and handling the Practice tab
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
            
            # Update dropdown choices for box plot in Practice tab
            ui.update_select("plot_type", choices=["", "Histogram", "Box Plot", "Scatter Plot", "Bar Plot"])
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
        return ui.div()

    @output
    @render.ui
    def variable_input():
        df = uploaded_data.get()
        plot_type = input.plot_type()

        if df is not None and plot_type:
            numeric_vars = df.select_dtypes(include=np.number).columns.tolist()
            categorical_vars = df.select_dtypes(include='object').columns.tolist()

            if plot_type == "Histogram" :
                return ui.input_select("var_histogram", "Select variable for Histogram:", 
                                       choices=[""] + numeric_vars)

            if plot_type == "Box Plot":
                return ui.div(
                    ui.input_select("var_boxplot_x", "Select numerical variable for X-axis:", choices=[""] + numeric_vars),
                    ui.input_select("var_boxplot_y", "Select categorical variable for Y-axis (optional):", choices=[""] + categorical_vars, selected="")
                )
            elif plot_type == "Scatter Plot":
                return ui.div(
                    ui.input_select("var_scatter_x", "Select X variable:", 
                                    choices=[""] + numeric_vars),
                    ui.input_select("var_scatter_y", "Select Y variable:", 
                                    choices=[""] + numeric_vars)
                )
            elif plot_type == "Bar Plot":
                return ui.input_select(f"var_bar_plot", 
                                       f"Select variable for Bar Plot:", 
                                       choices=[""] + categorical_vars)
        return ui.div()
    
    @reactive.Effect
    @reactive.event(input.var_scatter_x)
    def update_scatter_y_choices():
        df = uploaded_data.get()
        if df is not None and input.plot_type() == "Scatter Plot":
            numeric_vars = df.select_dtypes(include=np.number).columns.tolist()
            x_var = input.var_scatter_x()
            y_choices = [""] + [var for var in numeric_vars if var != x_var]
            ui.update_select("var_scatter_y", choices=y_choices)

    # Box Plot - If Y variable is not selected, render the plot with X only
    @output
    @render_maidr
    def create_custom_plot():
        df = uploaded_data.get()
        plot_type = input.plot_type()
        color = color_palettes[input.plot_color()]  # Get selected color for plot

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
                    sns.boxplot(x=var_x, y=var_y, data=df, palette=[color], ax=ax)
                    ax.set_title(f"Box Plot of {var_x} grouped by {var_y}")
                    ax.set_xlabel(var_x.replace("_", " ").title())
                    ax.set_ylabel(var_y.replace("_", " ").title())
                elif var_x:
                    sns.boxplot(x=df[var_x], color=color, ax=ax)
                    ax.set_title(f"Box Plot of {var_x}")
                    ax.set_xlabel(var_x.replace("_", " ").title())
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

            return ax
        except Exception as e:
            print(f"Error generating plot: {str(e)}")
            return None


# Create the app
app = App(app_ui, server)

# Run the app
if __name__ == "__main__":
    app.run()