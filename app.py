import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import uuid
import os
import base64
import io
from pathlib import Path
from matplotlib.backends.backend_svg import FigureCanvasSVG
from maidr.widget.shiny import render_maidr
import maidr
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
from plots.multilayerplot import create_multilayer_plot, create_custom_multilayer_plot
from plots.multipanelplot import create_multipanel_plot, create_custom_multipanel_plot
from plots.candlestick import create_candlestick

# Import help menu module
from HelpMenu import get_help_modal, QUICK_HELP_TIPS

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
            .sr-only {
                position: absolute;
                width: 1px;
                height: 1px;
                padding: 0;
                margin: -1px;
                overflow: hidden;
                clip: rect(0, 0, 0, 0);
                white-space: nowrap;
                border: 0;
            }
            #aria-announcements {
                position: absolute;
                left: -10000px;
                width: 1px;
                height: 1px;
                overflow: hidden;
            }
        """
        ),
        ui.tags.script(
            """
            Shiny.addCustomMessageHandler("update_theme", function(theme) {
                document.body.classList.toggle("dark-theme", theme === "Dark");
                document.body.classList.toggle("light-theme", theme === "Light");
                
                // Announce theme change
                var announcement = "Theme changed to " + theme + " mode";
                announceToScreenReader(announcement);
            });
            
            Shiny.addCustomMessageHandler("announce", function(message) {
                announceToScreenReader(message);
            });
            
            Shiny.addCustomMessageHandler("show_help", function(message) {
                // Trigger the help modal
                Shiny.setInputValue("show_help_modal", Math.random());
            });
            
            function announceToScreenReader(message) {
                var ariaLive = document.getElementById('aria-announcements');
                if (!ariaLive) {
                    ariaLive = document.createElement('div');
                    ariaLive.id = 'aria-announcements';
                    ariaLive.setAttribute('aria-live', 'polite');
                    ariaLive.setAttribute('aria-atomic', 'true');
                    ariaLive.style.position = 'absolute';
                    ariaLive.style.left = '-10000px';
                    ariaLive.style.width = '1px';
                    ariaLive.style.height = '1px';
                    ariaLive.style.overflow = 'hidden';
                    document.body.appendChild(ariaLive);
                }
                
                // Clear previous message and add new one
                ariaLive.textContent = '';
                setTimeout(function() {
                    ariaLive.textContent = message;
                }, 100);
            }
            
            // Announce when plots are loaded
            document.addEventListener('DOMContentLoaded', function() {
                // Watch for plot updates
                var observer = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                            for (var i = 0; i < mutation.addedNodes.length; i++) {
                                var node = mutation.addedNodes[i];
                                if (node.nodeType === 1) { // Element node
                                    if (node.querySelector && node.querySelector('svg, canvas, img')) {
                                        announceToScreenReader('Plot has been updated and is now available for exploration');
                                        break;
                                    }
                                }
                            }
                        }
                    });
                });
                
                // Start observing
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
                
                // Add keyboard event listener for help menu
                document.addEventListener('keydown', function(event) {
                    var activeElement = document.activeElement;
                    var isInputField = activeElement && (
                        activeElement.tagName === 'INPUT' || 
                        activeElement.tagName === 'TEXTAREA' || 
                        activeElement.tagName === 'SELECT' ||
                        activeElement.isContentEditable
                    );
                    
                    // Check if 'h' key is pressed (not in input fields)
                    if (event.key === 'h' || event.key === 'H') {
                        // Only trigger help if not in an input field
                        if (!isInputField) {
                            event.preventDefault();
                            
                            // Check if help modal is currently open
                            var helpModal = document.querySelector('#help_modal');
                            var isModalOpen = helpModal && helpModal.style.display !== 'none' && 
                                            helpModal.classList.contains('show');
                            
                            if (isModalOpen) {
                                // If modal is open, close it
                                Shiny.setInputValue("close_help", Math.random());
                                announceToScreenReader('Help menu closed.');
                            } else {
                                // If modal is closed, open it
                                Shiny.setInputValue("show_help_modal", Math.random());
                                announceToScreenReader('Help menu opened. Use Tab to navigate through help sections.');
                            }
                        }
                    }
                    
                    // Check if ESC key is pressed to close help menu
                    if (event.key === 'Escape') {
                        var helpModal = document.querySelector('#help_modal');
                        var isModalOpen = helpModal && helpModal.style.display !== 'none' && 
                                        helpModal.classList.contains('show');
                        
                        if (isModalOpen) {
                            event.preventDefault();
                            Shiny.setInputValue("close_help", Math.random());
                            announceToScreenReader('Help menu closed.');
                        }
                    }
                });
            });
        """
        ),
    ),
    # ARIA live region for announcements
    ui.div(
        id="aria-announcements",
        role="status",
        **{"aria-live": "polite", "aria-atomic": "true"},
        class_="sr-only"
    ),
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
            ),
            ui.nav_control(
                ui.input_action_button(
                    "save_html_button", 
                    "Save HTML", 
                    class_="btn btn-secondary",
                    style="margin-left: 10px;"
                )
            ),
            ui.nav_control(
                ui.input_action_button(
                    "help_button", 
                    "📚 Help (h)", 
                    class_="btn btn-info",
                    style="margin-left: 10px;",
                    title="Open help menu - keyboard shortcut: press 'h'"
                )
            ),
        ),
        # Fifth tab: Practice tab with file upload, data types, and custom plot creation
        ui.nav_panel(
            "Create your own Custom Plot",
            ui.row(
                # Left column for file upload, table, and conditional dropdowns (40% width)
                ui.column(
                    2,
                    ui.input_file("file_upload", "Upload CSV File", accept=".csv"),
                    ui.output_table("data_types"),
                    ui.output_ui("plot_options"),  # Conditionally render dropdowns
                    ui.output_ui("variable_input"),  # Variable input for specific plot
                ),
                # Right column for the plot (80% width)
                ui.column(10, 
                    ui.div(
                        ui.input_action_button("save_svg_button", "Save SVG to Downloads", 
                                              class_="btn btn-primary"),
                        class_="text-center mb-3"
                    ),
                    ui.div(
                        ui.output_ui("create_custom_plot"),
                        style="width: 100%; max-width: 800px;"
                    )
                ),
            ),
        ),
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
                selected="Default",
            ),
            ui.output_ui("create_histogram_output"),
        ),
        # Second tab: Box Plot with a single variable for Tutorial
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
                selected="Default",
            ),
            ui.output_ui("create_boxplot_output"),
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
                selected="Default",
            ),
            ui.output_ui("create_scatterplot_output"),
        ),
        # Fourth tab: Bar Plot with dropdowns and plot
        ui.nav_panel(
            "Bar Plot",
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
            "Line Plot",
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
            "Heatmap",
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
            "Multiline Plot",
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
        # New tab: Multilayer Plot
        ui.nav_panel(
            "Multilayer Plot",
            ui.input_select(
                "multilayer_background_type",
                "Select background plot type:",
                choices=[
                    "Bar Plot",
                    "Histogram",
                    "Scatter Plot"
                ],
                selected="Bar Plot",
            ),
            ui.input_select(
                "multilayer_background_color",
                "Select background color:",
                choices=list(color_palettes.keys()),
                selected="Default",
            ),
            ui.input_select(
                "multilayer_line_color",
                "Select line color:",
                choices=list(color_palettes.keys()),
                selected="Default",
            ),
            ui.output_ui("create_multilayer_plot_output"),
        ),
        
        # New tab: Multipanel Plot
        ui.nav_panel(
            "Multipanel Plot",
            ui.p("Three-panel plot with line plot and bar plots"),
            ui.output_ui("create_multipanel_plot_output"),
        ),
        
        # New tab: Candlestick Chart
        ui.nav_panel(
            "Candlestick Chart",
            ui.input_select(
                "candlestick_company",
                "Select company:",
                choices=[
                    "Tesla",
                    "Apple", 
                    "NVIDIA",
                    "Microsoft",
                    "Google",
                    "Amazon",
                ],
                selected="Tesla",
            ),
            ui.input_select(
                "candlestick_timeframe",
                "Select timeframe:",
                choices=[
                    "Daily",
                    "Monthly",
                    "Yearly",
                ],
                selected="Daily",
            ),
            ui.output_ui("create_candlestick_output"),
        ),
        
    ),
)


# Define the server logic
def server(input, output, session):
    uploaded_data = reactive.Value(None)
    # Add a reactive value to store multiline plot data
    multiline_data = reactive.Value(None)
    # Add reactive value to store the current figure
    current_figure = reactive.Value(None)
    # Add reactive value to store the current maidr object
    current_maidr = reactive.Value(None)

    # Helper function to announce messages to screen readers
    async def announce_to_screen_reader(message):
        """Send ARIA announcements to screen readers"""
        await session.send_custom_message("announce", message)

    # Handle help modal display
    @reactive.effect
    @reactive.event(input.show_help_modal)
    async def show_help():
        """Display the help modal when triggered"""
        modal = get_help_modal()
        ui.modal_show(modal)
        await announce_to_screen_reader("Help menu is now open. Navigate through sections using Tab key.")

    # Handle help modal close
    @reactive.effect
    @reactive.event(input.close_help)
    async def close_help():
        """Close the help modal"""
        ui.modal_remove()
        await announce_to_screen_reader("Help menu closed. You can press 'h' anytime to reopen it.")

    # Handle help button click
    @reactive.effect
    @reactive.event(input.help_button)
    async def help_button_clicked():
        """Show help modal when help button is clicked"""
        modal = get_help_modal()
        ui.modal_show(modal)
        await announce_to_screen_reader("Help menu opened via button click. Navigate through sections using Tab key.")

    # Update the theme based on the selected option
    @reactive.effect
    @reactive.event(input.theme)
    async def update_theme():
        await session.send_custom_message("update_theme", input.theme())

    # Add reactive effects to announce changes to screen readers
    @reactive.effect
    async def announce_plot_type_change():
        if uploaded_data.get() is not None and input.plot_type():
            plot_type = input.plot_type()
            await announce_to_screen_reader(f"Plot type changed to {plot_type}. Please select appropriate variables for this plot type.")
    
    @reactive.effect
    async def announce_histogram_changes():
        distribution_type = input.distribution_type()
        hist_color = input.hist_color()
        if distribution_type and hist_color:
            await announce_to_screen_reader(f"Histogram settings updated: {distribution_type} distribution with {hist_color} colors")

    @reactive.effect
    async def announce_boxplot_changes():
        boxplot_type = input.boxplot_type()
        boxplot_color = input.boxplot_color()
        if boxplot_type and boxplot_color:
            await announce_to_screen_reader(f"Box plot settings updated: {boxplot_type} with {boxplot_color} colors")

    @reactive.effect
    async def announce_scatter_changes():
        scatterplot_type = input.scatterplot_type()
        scatter_color = input.scatter_color()
        if scatterplot_type and scatter_color:
            await announce_to_screen_reader(f"Scatter plot settings updated: {scatterplot_type} with {scatter_color} colors")

    # Histogram Plot
    @output
    @render_maidr
    async def create_histogram_output():
        # Explicitly reference all relevant inputs for reactivity
        distribution_type = input.distribution_type()
        hist_color = input.hist_color()
        theme = input.theme()
        # Announce plot generation
        await announce_to_screen_reader(f"Generating {distribution_type.lower()} histogram with {hist_color.lower()} color scheme")
        
        result = create_histogram(distribution_type, hist_color, theme)
        
        # Store the current figure for HTML saving using plt.gcf()
        if result is not None:
            current_figure.set(plt.gcf())
            
        # Announce plot completion
        await announce_to_screen_reader(f"Histogram plot completed. Showing {distribution_type.lower()} distribution. Plot is now accessible for exploration.")
        return result

    # Box Plot
    @output
    @render_maidr
    async def create_boxplot_output():
        boxplot_type = input.boxplot_type()
        boxplot_color = input.boxplot_color()
        theme = input.theme()
        
        # Announce plot generation
        await announce_to_screen_reader(f"Generating {boxplot_type.lower()} box plot with {boxplot_color.lower()} color scheme")
        
        result = create_boxplot(boxplot_type, boxplot_color, theme)
        
        # Store the current figure for HTML saving using plt.gcf()
        if result is not None:
            current_figure.set(plt.gcf())
        
        # Announce plot completion
        await announce_to_screen_reader(f"Box plot completed. Showing {boxplot_type.lower()}. Plot is now accessible for exploration.")
        
        return result

    # Scatter Plot
    @output
    @render_maidr
    async def create_scatterplot_output():
        scatterplot_type = input.scatterplot_type()
        scatter_color = input.scatter_color()
        theme = input.theme()
        
        # Announce plot generation
        await announce_to_screen_reader(f"Generating scatter plot showing {scatterplot_type.lower()} with {scatter_color.lower()} color scheme")
        
        result = create_scatterplot(scatterplot_type, scatter_color, theme)
        
        # Store the current figure for HTML saving using plt.gcf()
        if result is not None:
            current_figure.set(plt.gcf())
        
        # Announce plot completion
        await announce_to_screen_reader(f"Scatter plot completed. Showing {scatterplot_type.lower()}. Plot is now accessible for exploration.")
        
        return result

    # Bar Plot
    @output
    @render_maidr
    async def create_barplot_output():
        barplot_color = input.barplot_color()
        theme = input.theme()
        
        # Announce plot generation
        await announce_to_screen_reader(f"Generating bar plot with {barplot_color.lower()} color scheme")
        
        result = create_barplot(barplot_color, theme)
        
        # Store the current figure for HTML saving using plt.gcf()
        if result is not None:
            current_figure.set(plt.gcf())
        
        # Announce plot completion
        await announce_to_screen_reader("Bar plot completed. Plot is now accessible for exploration.")
        
        return result

    # Line Plot
    @output
    @render_maidr
    async def create_lineplot_output():
        lineplot_type = input.lineplot_type()
        lineplot_color = input.lineplot_color()
        theme = input.theme()
        
        # Announce plot generation
        await announce_to_screen_reader(f"Generating line plot showing {lineplot_type.lower()} with {lineplot_color.lower()} color scheme")
        
        result = create_lineplot(lineplot_type, lineplot_color, theme)
        
        # Store the current figure for HTML saving using plt.gcf()
        if result is not None:
            current_figure.set(plt.gcf())
        
        # Announce plot completion
        await announce_to_screen_reader(f"Line plot completed. Showing {lineplot_type.lower()}. Plot is now accessible for exploration.")
        
        return result

    # Heatmap
    @output
    @render_maidr
    async def create_heatmap_output():
        heatmap_type = input.heatmap_type()
        theme = input.theme()
        
        # Announce plot generation
        await announce_to_screen_reader(f"Generating {heatmap_type.lower()} heatmap")
        
        result = create_heatmap(heatmap_type, theme)
        
        # Store the current figure for HTML saving using plt.gcf()
        if result is not None:
            current_figure.set(plt.gcf())
        
        # Announce plot completion
        await announce_to_screen_reader(f"Heatmap completed. Showing {heatmap_type.lower()} pattern. Plot is now accessible for exploration.")
        
        return result

    # Multiline Plot
    # First, create a reactive calculation for the multiline data
    @reactive.Calc
    def get_multiline_data():
        return generate_multiline_data(input.multiline_type())
    
    @output
    @render_maidr
    def create_multiline_plot_output():
        # Explicitly reference all relevant inputs for reactivity
        multiline_type = input.multiline_type()
        multiline_color = input.multiline_color()
        theme = input.theme()
        # Get the data using the reactive calculation
        data = get_multiline_data()
        result = create_multiline_plot(data, multiline_type, multiline_color, theme)
        
        # Store the current figure for HTML saving using plt.gcf()
        if result is not None:
            current_figure.set(plt.gcf())
            
        return result

    # Multilayer Plot
    @output
    @render_maidr
    def create_multilayer_plot_output():
        multilayer_background_type = input.multilayer_background_type()
        multilayer_background_color = input.multilayer_background_color()
        multilayer_line_color = input.multilayer_line_color()
        theme = input.theme()
        result = create_multilayer_plot(
            multilayer_background_type, 
            multilayer_background_color, 
            multilayer_line_color, 
            theme
        )
        
        # Store the current figure for HTML saving using plt.gcf()
        if result is not None:
            current_figure.set(plt.gcf())
            
        return result

    # Multipanel Plot
    @output
    @render_maidr
    def create_multipanel_plot_output():
        theme = input.theme()
        
        # Clear any existing figures first
        plt.clf()
        
        result = create_multipanel_plot("Column", "Default", theme)
        
        # Store the current figure for HTML saving - try multiple approaches
        if result is not None:
            try:
                # First try to get figure from the axes object
                fig = result.get_figure()
                current_figure.set(fig)
                print(f"Multipanel: Successfully captured figure with {len(fig.axes)} axes")
            except Exception as e:
                print(f"Multipanel: Error getting figure from axes: {e}")
                try:
                    # Fallback to plt.gcf()
                    fig = plt.gcf()
                    if fig and fig.axes:
                        current_figure.set(fig)
                        print(f"Multipanel: Fallback captured figure with {len(fig.axes)} axes")
                    else:
                        print("Multipanel: No valid figure found")
                except Exception as e2:
                    print(f"Multipanel: Fallback also failed: {e2}")
            
        return result

    # Candlestick Chart
    @output
    @render_maidr 
    def create_candlestick_output():
        try:
            candlestick_company = input.candlestick_company()
            candlestick_timeframe = input.candlestick_timeframe()
            theme = input.theme()
            
            # Create the candlestick plot
            ax = create_candlestick(candlestick_company, candlestick_timeframe, theme)
            
            if ax is None:
                return None
                
            # Store the current figure for HTML saving using plt.gcf()
            current_figure.set(plt.gcf())
            
            # For MAIDR rendering, return the axes object directly
            return ax
            
        except Exception as e:
            return None

    # Practice Tab Logic
    @reactive.Effect
    @reactive.event(input.file_upload)
    async def update_variable_choices():
        file: list[FileInfo] = input.file_upload()
        if file and len(file) > 0:
            # Announce file upload start
            await announce_to_screen_reader("Processing uploaded CSV file...")
            
            df = pd.read_csv(file[0]["datapath"])
            uploaded_data.set(df)
            numeric_vars = df.select_dtypes(include=np.number).columns.tolist()
            categorical_vars = df.select_dtypes(include="object").columns.tolist()
            
            # Announce successful file processing
            total_vars = len(df.columns)
            rows_count = len(df)
            await announce_to_screen_reader(f"File uploaded successfully. Dataset contains {rows_count} rows and {total_vars} variables: {len(numeric_vars)} numeric and {len(categorical_vars)} categorical variables.")

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
                    "Multilayer Plot",
                    "Multipanel Plot"
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
                        "Multiline Plot",
                        "Multilayer Plot",
                        "Multipanel Plot"
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
            elif plot_type == "Multilayer Plot":
                return ui.div(
                    ui.input_select(
                        "var_multilayer_x", 
                        "Select X variable (categorical):", 
                        choices=[""] + categorical_vars + numeric_vars
                    ),
                    ui.input_select(
                        "var_multilayer_background", 
                        "Select Background variable (numeric):", 
                        choices=[""] + numeric_vars
                    ),
                    ui.input_select(
                        "var_multilayer_line", 
                        "Select Line variable (numeric):", 
                        choices=[""] + numeric_vars
                    ),
                    ui.input_select(
                        "multilayer_background_type", 
                        "Select background plot type:", 
                        choices=["Bar Plot", "Histogram", "Scatter Plot"],
                        selected="Bar Plot"
                    ),
                    ui.input_select(
                        "multilayer_background_color",
                        "Select background color:",
                        choices=list(color_palettes.keys()),
                        selected="Default",
                    ),
                    ui.input_select(
                        "multilayer_line_color",
                        "Select line color:",
                        choices=list(color_palettes.keys()),
                        selected="Default",
                    )
                )
            elif plot_type == "Multipanel Plot":
                return ui.div(
                    ui.input_select(
                        "multipanel_layout_custom", 
                        "Select layout type:", 
                        choices=["Grid 2x2", "Row", "Column", "Mixed"],
                        selected="Grid 2x2"
                    ),
                    ui.input_select(
                        "multipanel_color_custom",
                        "Select color palette:",
                        choices=["Default", "Colorful", "Pastel", "Dark Tones", "Paired Colors", "Rainbow"],
                        selected="Default",
                    ),
                    ui.h4("Subplot 1:"),
                    ui.input_select(
                        "multipanel_plot1_type", 
                        "Plot type:", 
                        choices=["line", "bar", "scatter", "hist", "multiline"],
                        selected="line"
                    ),
                    ui.input_select(
                        "multipanel_plot1_x", 
                        "X variable:", 
                        choices=[""] + all_vars
                    ),
                    ui.input_select(
                        "multipanel_plot1_y", 
                        "Y variable:", 
                        choices=[""] + numeric_vars
                    ),
                    ui.input_select(
                        "multipanel_plot1_group", 
                        "Group variable (for multiline):", 
                        choices=[""] + categorical_vars
                    ),
                    ui.h4("Subplot 2:"),
                    ui.input_select(
                        "multipanel_plot2_type", 
                        "Plot type:", 
                        choices=["line", "bar", "scatter", "hist", "multiline"],
                        selected="bar"
                    ),
                    ui.input_select(
                        "multipanel_plot2_x", 
                        "X variable:", 
                        choices=[""] + all_vars
                    ),
                    ui.input_select(
                        "multipanel_plot2_y", 
                        "Y variable:", 
                        choices=[""] + numeric_vars
                    ),
                    ui.input_select(
                        "multipanel_plot2_group", 
                        "Group variable (for multiline):", 
                        choices=[""] + categorical_vars
                    ),
                    ui.h4("Subplot 3:"),
                    ui.input_select(
                        "multipanel_plot3_type", 
                        "Plot type:", 
                        choices=["line", "bar", "scatter", "hist", "multiline"],
                        selected="scatter"
                    ),
                    ui.input_select(
                        "multipanel_plot3_x", 
                        "X variable:", 
                        choices=[""] + all_vars
                    ),
                    ui.input_select(
                        "multipanel_plot3_y", 
                        "Y variable:", 
                        choices=[""] + numeric_vars
                    ),
                    ui.input_select(
                        "multipanel_plot3_group", 
                        "Group variable (for multiline):", 
                        choices=[""] + categorical_vars
                    ),
                    ui.h4("Subplot 4:"),
                    ui.input_select(
                        "multipanel_plot4_type", 
                        "Plot type:", 
                        choices=["line", "bar", "scatter", "hist", "multiline"],
                        selected="hist"
                    ),
                    ui.input_select(
                        "multipanel_plot4_x", 
                        "X variable:", 
                        choices=[""] + all_vars
                    ),
                    ui.input_select(
                        "multipanel_plot4_y", 
                        "Y variable:", 
                        choices=[""] + numeric_vars
                    ),
                    ui.input_select(
                        "multipanel_plot4_group", 
                        "Group variable (for multiline):", 
                        choices=[""] + categorical_vars
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
    async def create_custom_plot():
        df = uploaded_data.get()
        plot_type = input.plot_type()
        
        if df is None or not plot_type:
            return None
            
        color = color_palettes[input.plot_color()]
        theme = input.theme()

        # Announce plot generation start
        await announce_to_screen_reader(f"Generating custom {plot_type.lower()} using your uploaded data...")

        try:
            fig = plt.figure()
            if plot_type == "Histogram":
                var = input.var_histogram()
                if not var:
                    await announce_to_screen_reader("Please select a variable for the histogram")
                    return None
                result = create_custom_histogram(df, var, color, theme)
                # Store the figure for download
                current_figure.set(plt.gcf())
                await announce_to_screen_reader(f"Custom histogram completed using variable {var}. Plot is now accessible for exploration.")
                return result
                
            elif plot_type == "Box Plot":
                var_x = input.var_boxplot_x()
                var_y = input.var_boxplot_y()
                if not var_x:
                    await announce_to_screen_reader("Please select an X variable for the box plot")
                    return None
                result = create_custom_boxplot(df, var_x, var_y, color, theme)
                current_figure.set(plt.gcf())
                var_info = f" by {var_y}" if var_y else ""
                await announce_to_screen_reader(f"Custom box plot completed using variable {var_x}{var_info}. Plot is now accessible for exploration.")
                return result
                
            elif plot_type == "Scatter Plot":
                var_x = input.var_scatter_x()
                var_y = input.var_scatter_y()
                if not var_x or not var_y:
                    await announce_to_screen_reader("Please select both X and Y variables for the scatter plot")
                    return None
                result = create_custom_scatterplot(df, var_x, var_y, color, theme)
                current_figure.set(plt.gcf())
                await announce_to_screen_reader(f"Custom scatter plot completed showing {var_x} versus {var_y}. Plot is now accessible for exploration.")
                return result
                
            elif plot_type == "Bar Plot":
                var = input.var_bar_plot()
                if not var:
                    await announce_to_screen_reader("Please select a variable for the bar plot")
                    return None
                result = create_custom_barplot(df, var, color, theme)
                current_figure.set(plt.gcf())
                await announce_to_screen_reader(f"Custom bar plot completed using variable {var}. Plot is now accessible for exploration.")
                return result
                
            elif plot_type == "Line Plot":
                var_x = input.var_line_x()
                var_y = input.var_line_y()
                if not var_x or not var_y:
                    await announce_to_screen_reader("Please select both X and Y variables for the line plot")
                    return None
                result = create_custom_lineplot(df, var_x, var_y, color, theme)
                current_figure.set(plt.gcf())
                await announce_to_screen_reader(f"Custom line plot completed showing {var_x} versus {var_y}. Plot is now accessible for exploration.")
                return result
                
            elif plot_type == "Heatmap":
                var_x = input.var_heatmap_x()
                var_y = input.var_heatmap_y()
                var_value = input.var_heatmap_value()
                if not var_x or not var_y or not var_value:
                    await announce_to_screen_reader("Please select X, Y, and value variables for the heatmap")
                    return None
                colorscale = input.heatmap_colorscale()
                result = create_custom_heatmap(df, var_x, var_y, var_value, colorscale, theme)
                current_figure.set(plt.gcf())
                return result
                
            elif plot_type == "Multiline Plot":
                var_x = input.var_multiline_x()
                var_y = input.var_multiline_y()
                var_group = input.var_multiline_group()
                palette = input.multiline_palette()
                result = create_custom_multiline_plot(df, var_x, var_y, var_group, palette, theme)
                current_figure.set(plt.gcf())
                return result
                
            elif plot_type == "Multilayer Plot":
                var_x = input.var_multilayer_x()
                var_background = input.var_multilayer_background()
                var_line = input.var_multilayer_line()
                background_type = input.multilayer_background_type()
                background_color = input.multilayer_background_color()
                line_color = input.multilayer_line_color()
                result = create_custom_multilayer_plot(
                    df, var_x, var_background, var_line, background_type, 
                    background_color, line_color, theme
                )
                current_figure.set(plt.gcf())
                return result
                
            elif plot_type == "Multipanel Plot":
                # Create config dictionary for multipanel plot
                vars_config = {
                    'plot1': {
                        'type': input.multipanel_plot1_type(),
                        'x': input.multipanel_plot1_x(),
                        'y': input.multipanel_plot1_y(),
                        'group': input.multipanel_plot1_group()
                    },
                    'plot2': {
                        'type': input.multipanel_plot2_type(),
                        'x': input.multipanel_plot2_x(),
                        'y': input.multipanel_plot2_y(),
                        'group': input.multipanel_plot2_group()
                    },
                    'plot3': {
                        'type': input.multipanel_plot3_type(),
                        'x': input.multipanel_plot3_x(),
                        'y': input.multipanel_plot3_y(),
                        'group': input.multipanel_plot3_group()
                    },
                    'plot4': {
                        'type': input.multipanel_plot4_type(),
                        'x': input.multipanel_plot4_x(),
                        'y': input.multipanel_plot4_y(),
                        'group': input.multipanel_plot4_group()
                    }
                }
                
                layout_type = input.multipanel_layout_custom()
                color_palette = input.multipanel_color_custom()
                
                result = create_custom_multipanel_plot(
                    df, vars_config, layout_type, color_palette, theme
                )
                # For multipanel plots, get figure from the axes object
                if result is not None:
                    current_figure.set(result.get_figure())
                return result
                
            return None
        except Exception as e:
            print(f"Error generating plot: {str(e)}")
            return None

    # Handle saving SVG to Downloads folder
    @reactive.effect
    @reactive.event(input.save_svg_button)
    async def save_svg_to_downloads():
        # Get the current figure
        fig = current_figure.get()
        
        if fig is None:
            await announce_to_screen_reader("No plot available to save")
            ui.notification_show("No plot available to save", type="warning")
            return
        
        # Announce save process start
        await announce_to_screen_reader("Saving plot as SVG file to Downloads folder...")
        
        try:
            # Create a unique filename with timestamp
            plot_type = input.plot_type() if input.plot_type() else "plot"
            filename = f"{plot_type.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}.svg"
            
            # Get the Downloads folder path
            downloads_folder = str(Path.home() / "Downloads")
            filepath = os.path.join(downloads_folder, filename)
            
            # Save the figure directly, avoid temporary figure creation
            fig.savefig(filepath, format='svg', bbox_inches='tight')
            
            await announce_to_screen_reader(f"SVG file saved successfully as {filename} in Downloads folder")
            ui.notification_show(f"Plot saved to Downloads as {filename}", type="success")
        except Exception as e:
            await announce_to_screen_reader(f"Error saving SVG file: {str(e)}")
            ui.notification_show(f"Error saving plot: {str(e)}", type="error")
            print(f"Error saving SVG: {str(e)}")

    # Handle saving HTML to Downloads folder
    @reactive.effect
    @reactive.event(input.save_html_button)
    async def save_html_to_downloads():
        # Announce save process start
        await announce_to_screen_reader("Saving accessible plot as HTML file to Downloads folder...")
        try:
            # Create a unique filename with timestamp
            filename = f"accessible_plot_{uuid.uuid4().hex[:8]}.html"
            
            # Get the Downloads folder path
            downloads_folder = str(Path.home() / "Downloads")
            filepath = os.path.join(downloads_folder, filename)
            
            # Get the current figure
            fig = current_figure.get()
            if fig is None:
                # Try to get the current plot from matplotlib
                fig = plt.gcf()
                if fig and fig.get_axes():
                    current_figure.set(fig)
                    print(f"Save HTML: Using fallback figure with {len(fig.axes)} axes")
                else:
                    await announce_to_screen_reader("No plot available to save")
                    ui.notification_show("No plot available to save", type="warning")
                    print("Save HTML: No valid figure found")
                    return
            else:
                print(f"Save HTML: Using stored figure with {len(fig.axes)} axes")
            
            # Save original environment encoding settings
            original_encoding = os.environ.get('PYTHONIOENCODING', '')
            
            try:
                # Set UTF-8 encoding for Python I/O operations
                os.environ['PYTHONIOENCODING'] = 'utf-8'
                
                # Try to set matplotlib to use UTF-8 compatible fonts
                import matplotlib
                matplotlib.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'Segoe UI', 'Tahoma', 'sans-serif']
                
                # Use maidr.save_html with environment set for UTF-8
                maidr.save_html(fig, filepath)
                
            except (UnicodeEncodeError, UnicodeDecodeError) as unicode_error:
                print(f"Unicode error occurred: {unicode_error}")
                # If there's a Unicode error, try alternative approach
                try:
                    # Save to a temporary file in a different location
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
                        temp_filepath = temp_file.name
                    
                    # Try saving to temp location first
                    maidr.save_html(fig, temp_filepath)
                    
                    # If successful, copy to final location with proper encoding
                    with open(temp_filepath, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                        
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Clean up temporary file
                    os.remove(temp_filepath)
                    
                except Exception as fallback_error:
                    print(f"Fallback method also failed: {fallback_error}")
                    raise unicode_error  # Re-raise the original Unicode error
                    
            finally:
                # Restore original encoding setting
                if original_encoding:
                    os.environ['PYTHONIOENCODING'] = original_encoding
                elif 'PYTHONIOENCODING' in os.environ:
                    del os.environ['PYTHONIOENCODING']
            
            await announce_to_screen_reader(f"Accessible HTML file saved successfully as {filename} in Downloads folder. This file includes screen reader compatible features.")
            ui.notification_show(f"Accessible plot saved to Downloads as {filename}", type="success")
            
        except Exception as e:
            await announce_to_screen_reader(f"Error saving HTML file: {str(e)}")
            ui.notification_show(f"Error saving HTML: {str(e)}", type="error")
            print(f"Error saving HTML: {str(e)}")

# Create the app
app = App(app_ui, server)

# Run the app
if __name__ == "__main__":
    app.run()
