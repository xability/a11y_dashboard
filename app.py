import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import uuid
import os
import tempfile
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

# Function to save HTML with UTF-8 encoding to avoid Windows encoding issues
def save_html_utf8(fig, filepath):
    """Save matplotlib figure as HTML with proper UTF-8 encoding"""
    import io
    import sys
    import codecs
    import os
    import builtins
    from contextlib import redirect_stdout, redirect_stderr
    
    # Store original open function
    original_open = builtins.open
    
    def utf8_open(*args, **kwargs):
        """Wrapper for open() that forces UTF-8 encoding for text files"""
        # If mode contains 'w' or 'a' and no encoding is specified, use UTF-8
        if len(args) >= 2:
            mode = args[1]
            if isinstance(mode, str) and ('w' in mode or 'a' in mode) and 'b' not in mode:
                if 'encoding' not in kwargs:
                    kwargs['encoding'] = 'utf-8'
        elif 'mode' in kwargs:
            mode = kwargs['mode']
            if isinstance(mode, str) and ('w' in mode or 'a' in mode) and 'b' not in mode:
                if 'encoding' not in kwargs:
                    kwargs['encoding'] = 'utf-8'
        
        return original_open(*args, **kwargs)
    
    # Capture stdout/stderr during maidr.save_html to avoid encoding issues
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    try:
        # Create temporary UTF-8 buffers
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        # Redirect to UTF-8 buffers during maidr.save_html
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            # Monkey patch the open function to force UTF-8
            builtins.open = utf8_open
            
            try:
                # Create temp file with UTF-8 encoding using codecs
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
                temp_path = temp_file.name
                temp_file.close()
                
                try:
                    # Try to save directly with monkey-patched open
                    maidr.save_html(fig, temp_path)
                    
                    # Verify the file was created and has content
                    if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                        # Read with codecs to ensure proper UTF-8 handling
                        with codecs.open(temp_path, 'r', encoding='utf-8', errors='replace') as temp_f:
                            content = temp_f.read()
                        
                        # Write to final destination with codecs for explicit UTF-8
                        with codecs.open(filepath, 'w', encoding='utf-8') as final_f:
                            final_f.write(content)
                    else:
                        raise Exception("MAIDR save_html produced no output or empty file")
                        
                except Exception as maidr_error:
                    print(f"Monkey-patched maidr.save_html failed: {maidr_error}")
                    
                    # Fallback: try saving with maidr to a different temp file and post-process
                    temp_path_fallback = temp_path + "_fallback"
                    
                    try:
                        # Let maidr save however it wants to the fallback path
                        maidr.save_html(fig, temp_path_fallback)
                        
                        # Read the file and re-encode as UTF-8
                        # Try multiple encodings to read the file
                        content = None
                        for encoding in ['utf-8', 'cp1252', 'latin1', 'ascii']:
                            try:
                                with open(temp_path_fallback, 'r', encoding=encoding, errors='replace') as f:
                                    content = f.read()
                                break
                            except UnicodeDecodeError:
                                continue
                        
                        if content is None:
                            raise Exception("Could not read saved HTML file with any encoding")
                        
                        # Write to final destination with explicit UTF-8
                        with codecs.open(filepath, 'w', encoding='utf-8') as final_f:
                            final_f.write(content)
                        
                        # Clean up fallback temp file
                        try:
                            os.unlink(temp_path_fallback)
                        except:
                            pass
                            
                    except Exception as fallback_error:
                        print(f"Fallback approach also failed: {fallback_error}")
                        raise Exception(f"All encoding workarounds failed: {maidr_error}, {fallback_error}")
                        
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
            finally:
                # Restore original open function
                builtins.open = original_open
                    
    finally:
        # Restore original stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr

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
            .embed-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                z-index: 1000;
                display: none;
            }
            .embed-modal-content {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                max-width: 80%;
                max-height: 80%;
                width: 600px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .embed-modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                border-bottom: 1px solid #dee2e6;
                padding-bottom: 10px;
            }
            .embed-modal-body textarea {
                width: 100%;
                height: 300px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #ccc;
                padding: 10px;
                resize: vertical;
            }
            .embed-modal-footer {
                margin-top: 15px;
                text-align: right;
            }
            .embed-modal-footer button {
                margin-left: 10px;
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
            
            Shiny.addCustomMessageHandler("download_file", function(data) {
                console.log('Download triggered for:', data.filename);
                
                try {
                    // Determine MIME type (default to HTML if not provided)
                    var mimeType = data.mime_type || 'text/html;charset=utf-8';
                    // Create a blob from the content
                    var blob = new Blob([data.content], { type: mimeType });
                    console.log('Blob created:', blob.size, 'bytes');
                    
                    // Check if the browser supports the download attribute
                    if (typeof document.createElement('a').download !== 'undefined') {
                        console.log('Using download attribute method');
                        
                        // Create a download link
                        var link = document.createElement('a');
                        var url = window.URL.createObjectURL(blob);
                        link.href = url;
                        link.download = data.filename;
                        link.style.display = 'none';
                        
                        // Add to document
                        document.body.appendChild(link);
                        console.log('Link added to document');
                        
                        // Trigger click immediately
                        link.click();
                        console.log('Link clicked');
                        
                        // Clean up after a short delay
                        setTimeout(function() {
                            try {
                                document.body.removeChild(link);
                                window.URL.revokeObjectURL(url);
                                console.log('Cleanup completed');
                            } catch (e) {
                                console.log('Cleanup error:', e);
                            }
                        }, 1000);
                        
                    } else {
                        console.log('Using fallback method');
                        // Fallback for older browsers
                        var url = window.URL.createObjectURL(blob);
                        var newWindow = window.open(url, '_blank');
                        if (!newWindow) {
                            console.log('Popup blocked, trying alternative');
                            // If popup is blocked, try alternative
                            window.location.href = url;
                        }
                        setTimeout(function() {
                            window.URL.revokeObjectURL(url);
                        }, 1000);
                    }
                    
                    announceToScreenReader('Download started: ' + data.filename);
                    
                    // Visual alert for users
                    try {
                        var alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-success alert-dismissible fade show';
                        alertDiv.setAttribute('role', 'alert');
                        alertDiv.style.position = 'fixed';
                        alertDiv.style.top = '20px';
                        alertDiv.style.right = '20px';
                        alertDiv.style.zIndex = 2000;
                        alertDiv.textContent = '✓ ' + data.filename + ' downloaded';

                        var closeBtn = document.createElement('button');
                        closeBtn.type = 'button';
                        closeBtn.className = 'btn-close';
                        closeBtn.setAttribute('aria-label', 'Close');
                        closeBtn.addEventListener('click', function() {
                            alertDiv.remove();
                        });
                        alertDiv.appendChild(closeBtn);

                        document.body.appendChild(alertDiv);
                        // Auto-dismiss after 4 s
                        setTimeout(function() {
                            try { alertDiv.classList.remove('show'); alertDiv.remove(); } catch(e) {}
                        }, 4000);
                    } catch(e) {
                        console.log('Could not create visual alert', e);
                    }
                    
                } catch (e) {
                    console.error('Download error:', e);
                    announceToScreenReader('Download failed: ' + e.message);
                }
            });
            
            Shiny.addCustomMessageHandler("copy_text_to_clipboard", function(text) {
                try {
                    navigator.clipboard.writeText(text).then(function() {
                        announceToScreenReader('Embed code copied to clipboard');
                        // Visual toast
                        var toast = document.createElement('div');
                        toast.className = 'alert alert-info alert-dismissible fade show';
                        toast.setAttribute('role', 'alert');
                        toast.style.position = 'fixed';
                        toast.style.top = '20px';
                        toast.style.right = '20px';
                        toast.style.zIndex = 2000;
                        toast.textContent = 'Embed code copied to clipboard';
                        var closeBtn = document.createElement('button');
                        closeBtn.type = 'button';
                        closeBtn.className = 'btn-close';
                        closeBtn.setAttribute('aria-label', 'Close');
                        closeBtn.addEventListener('click', function() { toast.remove(); });
                        toast.appendChild(closeBtn);
                        document.body.appendChild(toast);
                        setTimeout(function(){ try{toast.classList.remove('show'); toast.remove();}catch(e){} }, 4000);
                    });
                } catch(e) {
                    console.error('Clipboard copy failed', e);
                    announceToScreenReader('Failed to copy embed code');
                }
            });
            
            Shiny.addCustomMessageHandler("show_embed_modal", function(embedCode) {
                // Trigger showing the embed modal in Shiny
                Shiny.setInputValue("embed_code_content", embedCode);
                Shiny.setInputValue("show_embed_modal_trigger", Math.random());
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
                ui.div(
                    ui.input_action_button(
                        "help_button",
                        "📚 Help (h)",
                        class_="btn btn-info",
                        title="Open help menu - keyboard shortcut: press 'h'"
                    ),
                    style="display: flex; gap: 10px; margin-top: 10px;"
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
                        ui.input_action_button(
                            "download_graphics_custom",
                            "Download Graphics",
                            class_="btn btn-primary",
                        ),
                        ui.input_action_button(
                            "download_html_custom",
                            "Download Multimodal Plot",
                            class_="btn btn-secondary",
                        ),
                        ui.input_action_button(
                            "embed_code_button_custom",
                            "Embed Code",
                            class_="btn btn-success",
                            aria_label="Get embed code for your website",
                        ),
                        class_="text-center mb-3",
                        style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;"
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
            ui.div(
                ui.input_action_button(
                    "download_graphics_histogram",
                    "Download Graphics",
                    class_="btn btn-primary",
                ),
                ui.input_action_button(
                    "download_html_histogram",
                    "Download Multimodal Plot",
                    class_="btn btn-secondary",
                ),
                ui.input_action_button(
                    "embed_code_button_histogram",
                    "Embed Code",
                    class_="btn btn-success",
                    aria_label="Get embed code for your website",
                ),
                class_="text-center mb-3",
                style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;"
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
            ui.div(
                ui.input_action_button(
                    "download_graphics_boxplot",
                    "Download Graphics",
                    class_="btn btn-primary",
                ),
                ui.input_action_button(
                    "download_html_boxplot",
                    "Download Multimodal Plot",
                    class_="btn btn-secondary",
                ),
                ui.input_action_button(
                    "embed_code_button_boxplot",
                    "Embed Code",
                    class_="btn btn-success",
                    aria_label="Get embed code for your website",
                ),
                class_="text-center mb-3",
                style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;"
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
            ui.div(
                ui.input_action_button(
                    "download_graphics_scatter",
                    "Download Graphics",
                    class_="btn btn-primary",
                ),
                ui.input_action_button(
                    "download_html_scatter",
                    "Download Multimodal Plot",
                    class_="btn btn-secondary",
                ),
                ui.input_action_button(
                    "embed_code_button_scatter",
                    "Embed Code",
                    class_="btn btn-success",
                    aria_label="Get embed code for your website",
                ),
                class_="text-center mb-3",
                style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;"
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
            ui.div(
                ui.input_action_button(
                    "download_graphics_barplot",
                    "Download Graphics",
                    class_="btn btn-primary",
                ),
                ui.input_action_button(
                    "download_html_barplot",
                    "Download Multimodal Plot",
                    class_="btn btn-secondary",
                ),
                ui.input_action_button(
                    "embed_code_button_barplot",
                    "Embed Code",
                    class_="btn btn-success",
                    aria_label="Get embed code for your website",
                ),
                class_="text-center mb-3",
                style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;"
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
            ui.div(
                ui.input_action_button(
                    "download_graphics_lineplot",
                    "Download Graphics",
                    class_="btn btn-primary",
                ),
                ui.input_action_button(
                    "download_html_lineplot",
                    "Download Multimodal Plot",
                    class_="btn btn-secondary",
                ),
                ui.input_action_button(
                    "embed_code_button_lineplot",
                    "Embed Code",
                    class_="btn btn-success",
                    aria_label="Get embed code for your website",
                ),
                class_="text-center mb-3",
                style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;"
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
            ui.div(
                ui.input_action_button(
                    "download_graphics_heatmap",
                    "Download Graphics",
                    class_="btn btn-primary",
                ),
                ui.input_action_button(
                    "download_html_heatmap",
                    "Download Multimodal Plot",
                    class_="btn btn-secondary",
                ),
                ui.input_action_button(
                    "embed_code_button_heatmap",
                    "Embed Code",
                    class_="btn btn-success",
                    aria_label="Get embed code for your website",
                ),
                class_="text-center mb-3",
                style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;"
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
            ui.div(
                ui.input_action_button(
                    "download_graphics_multiline",
                    "Download Graphics",
                    class_="btn btn-primary",
                ),
                ui.input_action_button(
                    "download_html_multiline",
                    "Download Multimodal Plot",
                    class_="btn btn-secondary",
                ),
                ui.input_action_button(
                    "embed_code_button_multiline",
                    "Embed Code",
                    class_="btn btn-success",
                    aria_label="Get embed code for your website",
                ),
                class_="text-center mb-3",
                style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;"
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
            ui.div(
                ui.input_action_button(
                    "download_graphics_multilayer",
                    "Download Graphics",
                    class_="btn btn-primary",
                ),
                ui.input_action_button(
                    "download_html_multilayer",
                    "Download Multimodal Plot",
                    class_="btn btn-secondary",
                ),
                ui.input_action_button(
                    "embed_code_button_multilayer",
                    "Embed Code",
                    class_="btn btn-success",
                    aria_label="Get embed code for your website",
                ),
                class_="text-center mb-3",
                style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;"
            ),
            ui.output_ui("create_multilayer_plot_output"),
        ),
        
        # New tab: Multipanel Plot
        ui.nav_panel(
            "Multipanel Plot",
            ui.p("Three-panel plot with line plot and bar plots"),
            ui.div(
                ui.input_action_button(
                    "download_graphics_multipanel",
                    "Download Graphics",
                    class_="btn btn-primary",
                ),
                ui.input_action_button(
                    "download_html_multipanel",
                    "Download Multimodal Plot",
                    class_="btn btn-secondary",
                ),
                ui.input_action_button(
                    "embed_code_button_multipanel",
                    "Embed Code",
                    class_="btn btn-success",
                    aria_label="Get embed code for your website",
                ),
                class_="text-center mb-3",
                style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;"
            ),
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
            ui.div(
                ui.input_action_button(
                    "download_graphics_candlestick",
                    "Download Graphics",
                    class_="btn btn-primary",
                ),
                ui.input_action_button(
                    "download_html_candlestick",
                    "Download Multimodal Plot",
                    class_="btn btn-secondary",
                ),
                ui.input_action_button(
                    "embed_code_button_candlestick",
                    "Embed Code",
                    class_="btn btn-success",
                    aria_label="Get embed code for your website",
                ),
                class_="text-center mb-3",
                style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;"
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
    
    # Reactive value to store the last saved file path
    last_saved_file = reactive.Value(None)

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

    # Generic function to handle embed code generation for any tab
    async def handle_embed_code_generation():
        """Generate embed code with full HTML content that preserves MAIDR functionality"""
        try:
            # Get the current figure
            fig = current_figure.get()
            if fig is None:
                fig = plt.gcf()
            
            if not fig or not fig.get_axes():
                await announce_to_screen_reader("No plot available to generate embed code")
                return
            
            # Generate HTML content using the same logic as download - this works!
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
            temp_filepath = temp_file.name
            temp_file.close()
            
            try:
                # Use the same save_html_utf8 function that works for downloads
                print(f"Saving MAIDR HTML using save_html_utf8 function")
                save_html_utf8(fig, temp_filepath)
                
                # Read the HTML content with explicit UTF-8 encoding
                with open(temp_filepath, 'r', encoding='utf-8', errors='replace') as f:
                    html_content = f.read()
                
                print(f"Generated HTML content length: {len(html_content)}")
                
                # Extract only the inner content (div with link, script, and SVG) for embedding
                # This excludes DOCTYPE, html, head, and body tags
                embed_code = extract_embed_content(html_content)
                
                print(f"Generated embed code length: {len(embed_code)}")
                
                # Send the full HTML code to client side
                await session.send_custom_message("show_embed_modal", embed_code)
                await announce_to_screen_reader("Embed code modal opened with secure iframe ready to copy. Contains sandboxed content with full MAIDR accessibility.")
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_filepath)
                except:
                    pass
                    
        except Exception as e:
            await announce_to_screen_reader(f"Error generating embed code: {str(e)}")
            print(f"Embed code generation error: {e}")
            import traceback
            traceback.print_exc()

    # Handle embed code button clicks for all tabs
    @reactive.effect
    @reactive.event(input.embed_code_button_custom)
    async def embed_code_button_custom_clicked():
        await handle_embed_code_generation()

    @reactive.effect
    @reactive.event(input.embed_code_button_histogram)
    async def embed_code_button_histogram_clicked():
        await handle_embed_code_generation()

    @reactive.effect
    @reactive.event(input.embed_code_button_boxplot)
    async def embed_code_button_boxplot_clicked():
        await handle_embed_code_generation()

    @reactive.effect
    @reactive.event(input.embed_code_button_scatter)
    async def embed_code_button_scatter_clicked():
        await handle_embed_code_generation()

    @reactive.effect
    @reactive.event(input.embed_code_button_barplot)
    async def embed_code_button_barplot_clicked():
        await handle_embed_code_generation()

    @reactive.effect
    @reactive.event(input.embed_code_button_lineplot)
    async def embed_code_button_lineplot_clicked():
        await handle_embed_code_generation()

    @reactive.effect
    @reactive.event(input.embed_code_button_heatmap)
    async def embed_code_button_heatmap_clicked():
        await handle_embed_code_generation()

    @reactive.effect
    @reactive.event(input.embed_code_button_multiline)
    async def embed_code_button_multiline_clicked():
        await handle_embed_code_generation()

    @reactive.effect
    @reactive.event(input.embed_code_button_multilayer)
    async def embed_code_button_multilayer_clicked():
        await handle_embed_code_generation()

    @reactive.effect
    @reactive.event(input.embed_code_button_multipanel)
    async def embed_code_button_multipanel_clicked():
        await handle_embed_code_generation()

    @reactive.effect
    @reactive.event(input.embed_code_button_candlestick)
    async def embed_code_button_candlestick_clicked():
        await handle_embed_code_generation()

    # Store embed code content
    embed_code_content = reactive.Value("")

    # Handle showing embed modal
    @reactive.effect
    @reactive.event(input.show_embed_modal_trigger)
    async def show_embed_modal():
        """Show embed code modal"""
        embed_code = getattr(input, 'embed_code_content', lambda: "")()
        if embed_code:
            embed_code_content.set(embed_code)
            modal = ui.modal(
                ui.h3("Embed Code"),
                ui.div(
                    ui.p("Iframe embed code (sandboxed and secure):"),
                    ui.input_text_area(
                        "embed_code_display",
                        "",
                        value=embed_code,
                        rows=15,
                        width="100%"
                    ),
                ),
                footer=ui.div(
                    ui.input_action_button("copy_embed_button", "Copy to Clipboard", class_="btn btn-primary"),
                    ui.modal_button("Close")
                ),
                size="l",
                easy_close=True
            )
            ui.modal_show(modal)
            await announce_to_screen_reader("Embed code modal opened with secure iframe that preserves all MAIDR accessibility features. Ready to copy and paste.")

    # Copy-to-clipboard handler
    @reactive.effect
    @reactive.event(input.copy_embed_button)
    async def copy_embed_to_clipboard():
        code = embed_code_content.get()
        if code:
            await session.send_custom_message("copy_text_to_clipboard", code)
            await announce_to_screen_reader("Embed code copied to clipboard")

    # Update the theme based on the selected option
    @reactive.effect
    @reactive.event(input.theme)
    async def update_theme():
        await session.send_custom_message("update_theme", input.theme())

    # Generic function to create HTML content and trigger download
    async def trigger_html_download(plot_type_suffix):
        """Generate HTML content and trigger browser download with save dialog"""
        try:
            # Get the current figure
            fig = current_figure.get()
            if fig is None:
                fig = plt.gcf()
            
            if not fig or not fig.get_axes():
                await announce_to_screen_reader("No plot available to download")
                return
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
            temp_filepath = temp_file.name
            temp_file.close()
            
            try:
                # Save the HTML content with proper UTF-8 encoding
                save_html_utf8(fig, temp_filepath)
                
                # Read the HTML content
                with open(temp_filepath, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Generate filename
                filename = f"accessible_plot_{plot_type_suffix}_{uuid.uuid4().hex[:8]}.html"
                
                # Send to JavaScript for download
                await session.send_custom_message("download_file", {
                    "content": html_content,
                    "filename": filename
                })
                
                await announce_to_screen_reader(f"Download initiated for {filename}")
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_filepath)
                except:
                    pass
                    
        except Exception as e:
            await announce_to_screen_reader(f"Error downloading HTML: {str(e)}")
            print(f"Download HTML error: {e}")

    # Handle download button clicks for all tabs
    @reactive.effect
    @reactive.event(input.download_html_custom)
    async def download_html_custom_clicked():
        await trigger_html_download("custom")

    @reactive.effect
    @reactive.event(input.download_html_histogram)
    async def download_html_histogram_clicked():
        await trigger_html_download("histogram")

    @reactive.effect
    @reactive.event(input.download_html_boxplot)
    async def download_html_boxplot_clicked():
        await trigger_html_download("boxplot")

    @reactive.effect
    @reactive.event(input.download_html_scatter)
    async def download_html_scatter_clicked():
        await trigger_html_download("scatter")

    @reactive.effect
    @reactive.event(input.download_html_barplot)
    async def download_html_barplot_clicked():
        await trigger_html_download("barplot")

    @reactive.effect
    @reactive.event(input.download_html_lineplot)
    async def download_html_lineplot_clicked():
        await trigger_html_download("lineplot")

    @reactive.effect
    @reactive.event(input.download_html_heatmap)
    async def download_html_heatmap_clicked():
        await trigger_html_download("heatmap")

    @reactive.effect
    @reactive.event(input.download_html_multiline)
    async def download_html_multiline_clicked():
        await trigger_html_download("multiline")

    @reactive.effect
    @reactive.event(input.download_html_multilayer)
    async def download_html_multilayer_clicked():
        await trigger_html_download("multilayer")

    @reactive.effect
    @reactive.event(input.download_html_multipanel)
    async def download_html_multipanel_clicked():
        await trigger_html_download("multipanel")

    @reactive.effect
    @reactive.event(input.download_html_candlestick)
    async def download_html_candlestick_clicked():
        await trigger_html_download("candlestick")

    # Add remaining reactive effects and output functions here
    
    # Histogram plot rendering
    @output
    @render_maidr
    async def create_histogram_output():
        """Create and render histogram plot"""
        try:
            # Explicitly reference all relevant inputs for reactivity
            distribution_type = input.distribution_type()
            hist_color = input.hist_color()
            theme = input.theme()
            
            # Announce plot generation
            await announce_to_screen_reader(f"Generating {distribution_type.lower()} histogram with {hist_color.lower()} color scheme")
            
            ax = create_histogram(distribution_type, hist_color, theme)
            print(f"create_histogram returned: {type(ax)}, value: {ax}")
            
            if ax is not None:
                # Check if ax is actually an axes object, not a list
                if isinstance(ax, list):
                    print(f"ERROR: create_histogram returned a list instead of axes object: {type(ax)}, length: {len(ax)}")
                    return None
                
                # Check if it has the figure attribute
                if not hasattr(ax, 'figure'):
                    print(f"ERROR: create_histogram returned object without figure attribute: {type(ax)}")
                    return None
                    
                fig = ax.figure
                current_figure.set(fig)
                print(f"Returning to MAIDR: {type(ax)}, axes object: {ax}")
                # Return the axes object, not the figure - MAIDR expects the axes
                return ax
        except Exception as e:
            print(f"Error creating histogram: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # Box plot rendering
    @output
    @render_maidr
    def create_boxplot_output():
        """Create and render box plot"""
        try:
            ax = create_boxplot(input.boxplot_type(), input.boxplot_color(), input.theme())
            if ax is not None:
                # Check if ax is actually an axes object, not a list
                if isinstance(ax, list):
                    print(f"ERROR: create_boxplot returned a list instead of axes object: {type(ax)}")
                    return None
                fig = ax.figure
                current_figure.set(fig)
                return ax
        except Exception as e:
            print(f"Error creating boxplot: {e}")
            return None
    
    # Scatter plot rendering
    @output
    @render_maidr
    def create_scatterplot_output():
        """Create and render scatter plot"""
        try:
            ax = create_scatterplot(input.scatterplot_type(), input.scatter_color(), input.theme())
            if ax is not None:
                # Check if ax is actually an axes object, not a list
                if isinstance(ax, list):
                    print(f"ERROR: create_scatterplot returned a list instead of axes object: {type(ax)}")
                    return None
                fig = ax.figure
                current_figure.set(fig)
                return ax
        except Exception as e:
            print(f"Error creating scatterplot: {e}")
            return None
    
    # Bar plot rendering
    @output
    @render_maidr
    def create_barplot_output():
        """Create and render bar plot"""
        try:
            ax = create_barplot(input.barplot_color(), input.theme())
            if ax is not None:
                # Check if ax is actually an axes object, not a list
                if isinstance(ax, list):
                    print(f"ERROR: create_barplot returned a list instead of axes object: {type(ax)}")
                    return None
                fig = ax.figure
                current_figure.set(fig)
                return ax
        except Exception as e:
            print(f"Error creating barplot: {e}")
            return None
    
    # Line plot rendering
    @output
    @render_maidr
    def create_lineplot_output():
        """Create and render line plot"""
        try:
            ax = create_lineplot(input.lineplot_type(), input.lineplot_color(), input.theme())
            if ax is not None:
                # Check if ax is actually an axes object, not a list
                if isinstance(ax, list):
                    print(f"ERROR: create_lineplot returned a list instead of axes object: {type(ax)}")
                    return None
                fig = ax.figure
                current_figure.set(fig)
                return ax
        except Exception as e:
            print(f"Error creating lineplot: {e}")
            return None
    
    # Heatmap rendering
    @output
    @render_maidr
    def create_heatmap_output():
        """Create and render heatmap"""
        try:
            ax = create_heatmap(input.heatmap_type(), input.theme())
            if ax is not None:
                # Check if ax is actually an axes object, not a list
                if isinstance(ax, list):
                    print(f"ERROR: create_heatmap returned a list instead of axes object: {type(ax)}")
                    return None
                fig = ax.figure
                current_figure.set(fig)
                return ax
        except Exception as e:
            print(f"Error creating heatmap: {e}")
            return None
    
    # Multiline plot rendering
    @output
    @render_maidr
    def create_multiline_plot_output():
        """Create and render multiline plot"""
        try:
            data = generate_multiline_data(input.multiline_type())
            multiline_data.set(data)
            
            ax = create_multiline_plot(data, input.multiline_type(), input.multiline_color(), input.theme())
            if ax is not None:
                # Check if ax is actually an axes object, not a list
                if isinstance(ax, list):
                    print(f"ERROR: create_multiline_plot returned a list instead of axes object: {type(ax)}")
                    return None
                fig = ax.figure
                current_figure.set(fig)
                return ax
        except Exception as e:
            print(f"Error creating multiline plot: {e}")
            return None
    
    # Multilayer plot rendering
    @output
    @render_maidr
    def create_multilayer_plot_output():
        """Create and render multilayer plot"""
        try:
            ax = create_multilayer_plot(
                input.multilayer_background_type(), 
                input.multilayer_background_color(), 
                input.multilayer_line_color(), 
                input.theme()
            )
            if ax is not None:
                # Check if ax is actually an axes object, not a list
                if isinstance(ax, list):
                    print(f"ERROR: create_multilayer_plot returned a list instead of axes object: {type(ax)}")
                    return None
                fig = ax.figure
                current_figure.set(fig)
                return ax
        except Exception as e:
            print(f"Error creating multilayer plot: {e}")
            return None
    
    # Multipanel plot rendering
    @output
    @render_maidr
    def create_multipanel_plot_output():
        """Create and render multipanel plot"""
        try:
            ax = create_multipanel_plot("default", "default", input.theme())
            print(f"create_multipanel_plot returned: {type(ax)}, value: {ax}")
            
            if ax is not None:
                # Check if ax is actually an axes object, not a list
                if isinstance(ax, list):
                    print(f"ERROR: create_multipanel_plot returned a list instead of axes object: {type(ax)}, length: {len(ax)}")
                    return None
                
                # Check if it has the figure attribute
                if not hasattr(ax, 'figure'):
                    print(f"ERROR: create_multipanel_plot returned object without figure attribute: {type(ax)}")
                    return None
                    
                fig = ax.figure
                current_figure.set(fig)
                return ax
        except Exception as e:
            print(f"Error creating multipanel plot: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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

    # File upload handling
    @reactive.effect
    @reactive.event(input.file_upload)
    async def handle_file_upload():
        """Handle CSV file upload"""
        if input.file_upload() is not None:
            try:
                file_info = input.file_upload()[0]
                df = pd.read_csv(file_info["datapath"])
                uploaded_data.set(df)
                await announce_to_screen_reader(f"File uploaded successfully with {len(df)} rows and {len(df.columns)} columns")
            except Exception as e:
                await announce_to_screen_reader(f"Error uploading file: {str(e)}")
                print(f"File upload error: {e}")

    # Data types table
    @output
    @render.table
    def data_types():
        """Display data types of uploaded file"""
        df = uploaded_data.get()
        if df is not None:
            summary = pd.DataFrame({
                'Column': df.columns,
                'Type': [str(df[col].dtype) for col in df.columns],
                'Non-null': [df[col].count() for col in df.columns]
            })
            return summary
        return pd.DataFrame()

    # Plot options dropdown
    @output
    @render.ui
    def plot_options():
        """Render plot type selection dropdown"""
        df = uploaded_data.get()
        if df is not None:
            return ui.input_select(
                "plot_type",
                "Select plot type:",
                choices=[""] + [
                    "Histogram",
                    "Box Plot", 
                    "Scatter Plot",
                    "Bar Plot",
                    "Line Plot",
                    "Heatmap"
                ]
            )
        return ui.div()

    # Variable input based on plot type
    @output
    @render.ui
    def variable_input():
        """Render variable selection based on plot type"""
        df = uploaded_data.get()
        plot_type = getattr(input, 'plot_type', lambda: None)()
        
        if df is not None and plot_type:
            # Robust dtype detection – numeric vs non-numeric
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            categorical_cols = df.select_dtypes(exclude='number').columns.tolist()
            
            if plot_type == "Histogram":
                return ui.div(
                    ui.input_select("var_x", "Select numeric variable:", choices=[""] + numeric_cols),
                    ui.input_select("hist_custom_color", "Select color:", choices=list(color_palettes.keys()), selected="Default")
                )
            elif plot_type == "Box Plot":
                return ui.div(
                    ui.input_select("var_x", "Select numeric variable:", choices=[""] + numeric_cols),
                    ui.input_select("var_y", "Select grouping variable (optional):", choices=["None"] + categorical_cols, selected="None"),
                    ui.input_select("boxplot_custom_color", "Select color:", choices=list(color_palettes.keys()), selected="Default")
                )
            elif plot_type == "Scatter Plot":
                # Exclude selected X variable from Y choices
                var_x_current = getattr(input, 'var_x', lambda: "")()
                y_choices = [col for col in numeric_cols if col != var_x_current]
                return ui.div(
                    ui.input_select("var_x", "Select X variable:", choices=[""] + numeric_cols, selected=var_x_current),
                    ui.input_select("var_y", "Select Y variable:", choices=[""] + y_choices),
                    ui.input_select("scatter_custom_color", "Select color:", choices=list(color_palettes.keys()), selected="Default")
                )
            elif plot_type == "Bar Plot":
                return ui.div(
                    ui.input_select("var_x", "Select categorical variable:", choices=[""] + categorical_cols),
                    ui.input_select("barplot_custom_color", "Select color:", choices=list(color_palettes.keys()), selected="Default")
                )
            elif plot_type == "Line Plot":
                var_x_current = getattr(input, 'var_x', lambda: "")()
                y_choices = [col for col in numeric_cols if col != var_x_current]
                return ui.div(
                    ui.input_select("var_x", "Select X variable:", choices=[""] + numeric_cols, selected=var_x_current),
                    ui.input_select("var_y", "Select Y variable:", choices=[""] + y_choices),
                    ui.input_select("lineplot_custom_color", "Select color:", choices=list(color_palettes.keys()), selected="Default")
                )
            elif plot_type == "Heatmap":
                return ui.div(
                    ui.input_select("var_x", "Select X (categorical):", choices=[""] + categorical_cols),
                    ui.input_select("var_y", "Select Y (categorical):", choices=[""] + categorical_cols),
                    ui.input_select("var_value", "Select numeric value (optional):", choices=["None"] + numeric_cols, selected="None"),
                    ui.input_select("heatmap_custom_color", "Select color scale:", choices=list(color_palettes.keys()), selected="Default")
                )
        return ui.div()

    # Custom plot creation
    @output
    @render_maidr
    def create_custom_plot():
        """Create custom plot based on user data and selections"""
        df = uploaded_data.get()
        plot_type = getattr(input, 'plot_type', lambda: None)()
        
        if df is None or not plot_type or plot_type == "":
            return None
            
        try:
            ax = None
            
            if plot_type == "Histogram" and hasattr(input, 'var_x') and input.var_x() and input.var_x() != "":
                color = color_palettes.get(getattr(input, 'hist_custom_color', lambda: 'Default')(), 'skyblue')
                ax = create_custom_histogram(df, input.var_x(), color, input.theme())
                
            elif plot_type == "Box Plot" and hasattr(input, 'var_x') and input.var_x() and input.var_x() != "":
                color = color_palettes.get(getattr(input, 'boxplot_custom_color', lambda: 'Default')(), 'skyblue')
                var_y = getattr(input, 'var_y', lambda: 'None')()
                var_y = None if var_y == 'None' or var_y == "" else var_y
                ax = create_custom_boxplot(df, input.var_x(), var_y, color, input.theme())
                
            elif plot_type == "Scatter Plot" and hasattr(input, 'var_x') and hasattr(input, 'var_y') and input.var_x() and input.var_y() and input.var_x() != "" and input.var_y() != "" and input.var_x() != input.var_y():
                color = color_palettes.get(getattr(input, 'scatter_custom_color', lambda: 'Default')(), 'skyblue')
                ax = create_custom_scatterplot(df, input.var_x(), input.var_y(), color, input.theme())
                
            elif plot_type == "Bar Plot" and hasattr(input, 'var_x') and input.var_x() and input.var_x() != "":
                color = color_palettes.get(getattr(input, 'barplot_custom_color', lambda: 'Default')(), 'skyblue')
                ax = create_custom_barplot(df, input.var_x(), color, input.theme())
            
            elif plot_type == "Line Plot" and all(hasattr(input, v) for v in ['var_x','var_y']) and input.var_x() and input.var_y() and input.var_x() != input.var_y():
                color = color_palettes.get(getattr(input, 'lineplot_custom_color', lambda: 'Default')(), 'skyblue')
                ax = create_custom_lineplot(df, input.var_x(), input.var_y(), color, input.theme())
            
            elif plot_type == "Heatmap" and all(hasattr(input, v) for v in ['var_x','var_y']):
                var_x = input.var_x()
                var_y = input.var_y()
                var_value = getattr(input, 'var_value', lambda: 'None')()
                var_value = None if var_value == 'None' or var_value == '' else var_value
                colorscale = color_palettes.get(getattr(input, 'heatmap_custom_color', lambda: 'Default')(), 'YlGnBu')
                if var_x and var_y and var_x != '' and var_y != '' and var_x != var_y:
                    ax = create_custom_heatmap(df, var_x, var_y, var_value, colorscale, input.theme())
            
            if ax is not None:
                # Check if ax is actually an axes object, not a list
                if isinstance(ax, list):
                    print(f"ERROR: Custom plot function returned a list instead of axes object: {type(ax)}")
                    return None
                fig = ax.figure
                current_figure.set(fig)
                return ax
                
        except Exception as e:
            print(f"Error creating custom plot: {e}")
            return None

    # Generic SVG download handler and per-tab triggers
    async def trigger_svg_download(plot_type_suffix):
        """Generate SVG in-memory and send to browser for download."""
        try:
            fig = current_figure.get()
            if fig is None:
                fig = plt.gcf()
            if not fig or not fig.get_axes():
                await announce_to_screen_reader("No plot available to download")
                return

            import io, codecs
            buffer = io.StringIO()
            fig.savefig(buffer, format='svg', bbox_inches='tight')
            svg_content = buffer.getvalue()
            buffer.close()

            filename = f"accessible_plot_{plot_type_suffix}_{uuid.uuid4().hex[:8]}.svg"

            # Send to browser
            await session.send_custom_message("download_file", {
                "content": svg_content,
                "filename": filename,
                "mime_type": "image/svg+xml;charset=utf-8",
            })

            await announce_to_screen_reader(f"Download initiated for {filename}")

        except Exception as e:
            await announce_to_screen_reader(f"Error preparing graphics file: {str(e)}")
            print(f"SVG creation error: {e}")

    # Download Graphics button events for all tabs
    @reactive.effect
    @reactive.event(input.download_graphics_custom)
    async def download_graphics_custom_clicked():
        await trigger_svg_download("custom")

    @reactive.effect
    @reactive.event(input.download_graphics_histogram)
    async def download_graphics_histogram_clicked():
        await trigger_svg_download("histogram")

    @reactive.effect
    @reactive.event(input.download_graphics_boxplot)
    async def download_graphics_boxplot_clicked():
        await trigger_svg_download("boxplot")

    @reactive.effect
    @reactive.event(input.download_graphics_scatter)
    async def download_graphics_scatter_clicked():
        await trigger_svg_download("scatter")

    @reactive.effect
    @reactive.event(input.download_graphics_barplot)
    async def download_graphics_barplot_clicked():
        await trigger_svg_download("barplot")

    @reactive.effect
    @reactive.event(input.download_graphics_lineplot)
    async def download_graphics_lineplot_clicked():
        await trigger_svg_download("lineplot")

    @reactive.effect
    @reactive.event(input.download_graphics_heatmap)
    async def download_graphics_heatmap_clicked():
        await trigger_svg_download("heatmap")

    @reactive.effect
    @reactive.event(input.download_graphics_multiline)
    async def download_graphics_multiline_clicked():
        await trigger_svg_download("multiline")

    @reactive.effect
    @reactive.event(input.download_graphics_multilayer)
    async def download_graphics_multilayer_clicked():
        await trigger_svg_download("multilayer")

    @reactive.effect
    @reactive.event(input.download_graphics_multipanel)
    async def download_graphics_multipanel_clicked():
        await trigger_svg_download("multipanel")

    @reactive.effect
    @reactive.event(input.download_graphics_candlestick)
    async def download_graphics_candlestick_clicked():
        await trigger_svg_download("candlestick")

    # Add reactive effects to announce changes to screen readers
    @reactive.effect
    async def announce_plot_type_change():
        try:
            if uploaded_data.get() is not None and hasattr(input, 'plot_type') and input.plot_type() and input.plot_type() != "":
                plot_type = input.plot_type()
                await announce_to_screen_reader(f"Plot type changed to {plot_type}. Please select appropriate variables for this plot type.")
        except:
            pass
    
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

# Function to extract embed content from full HTML
def extract_embed_content(html_content):
    """Extract div content and wrap in iframe with sandbox for secure embedding"""
    import re
    import html
    
    # Find the content between <body> and </body>
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
    
    if body_match:
        body_content = body_match.group(1).strip()
    else:
        # Fallback: try to find the main div with MAIDR content
        # Look for the div that contains the link and script
        div_match = re.search(r'(<div[^>]*>.*?<link.*?maidr.*?<script.*?</script>.*?<div.*?</div>\s*</div>)', html_content, re.DOTALL | re.IGNORECASE)
        
        if div_match:
            body_content = div_match.group(1).strip()
        else:
            # If we can't parse it properly, return an error message
            return "<!-- Error: Could not extract embed content from generated HTML -->"
    
    # Create a complete HTML document for the iframe
    iframe_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
{body_content}
</body>
</html>'''
    
    # Escape the HTML for use in srcdoc attribute
    escaped_html = html.escape(iframe_html, quote=True)
    
    # Create iframe with sandbox attributes for security
    # Allow scripts and same-origin for MAIDR functionality while maintaining security
    iframe_embed = f'''<iframe 
    srcdoc="{escaped_html}"
    style="width: 100%; height: 600px; border: 1px solid #ccc; border-radius: 4px;"
    sandbox="allow-scripts allow-same-origin"
    title="Accessible Interactive Plot with MAIDR">
</iframe>'''
    
    return iframe_embed

# Create the Shiny app
app = App(app_ui, server)