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
import datetime
import re

# Import candlestick module
from plots.candlestick import (
    create_candlestick,
    create_tutorial_candlestick_basics,
    create_tutorial_trends_volatility,
    create_tutorial_reversal_breakout,
    create_tutorial_hammer_pattern,
    create_tutorial_shooting_star_pattern
)

# Import help menu module
from HelpMenu import get_help_modal, QUICK_HELP_TIPS

# Set random seed
np.random.seed(1000)

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

# Define the UI components for the candlestick dashboard
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
            /* Sticky footer styles */
            body {
                min-height: 100vh;
                margin: 0;
                display: flex;
                flex-direction: column;
            }
            .main-content {
                flex: 1 0 auto;
                min-height: calc(100vh - 60px);
                padding-bottom: 2rem;
            }
            /* Enhanced footer */
            footer.app-footer {
                flex-shrink: 0;
                width: 100%;
                background-color: #f8f9fa;
                padding: 1.25rem 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                box-shadow: 0 -2px 5px rgba(0,0,0,0.05);
                font-size: 0.9rem;
                border-top: 1px solid #dee2e6;
            }
            body.dark-theme footer.app-footer {
                background-color: #000000;
                color: #ffffff;
                border-top: 1px solid #444;
            }

            /* About section – logo on the left, text on the right */
            .about-section {
                max-width: 1000px;
                margin: 0 auto;
                display: flex;
                flex-direction: row;
                gap: 2rem;
                align-items: flex-start;
            }
            .about-logo {
                max-width: 220px;
                height: auto;
                flex-shrink: 0;
            }
            .about-text {
                flex: 1;
                text-align: left;
            }
            .about-text h2 {
                font-weight: 700;
            }
            .about-text p {
                font-size: 1.05rem;
                line-height: 1.6;
            }
            .about-text ul {
                list-style-type: disc;
                margin-left: 1.2rem;
            }
            .about-text a {
                color: #0d6efd;
            }
            .about-paragraph {
                font-size: 1.05rem;
                line-height: 1.6;
            }
            
            /* Tutorial content styling */
            .tutorial-content {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }
            .tutorial-module {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 2rem;
                margin-bottom: 2rem;
                border-left: 4px solid #0d6efd;
            }
            body.dark-theme .tutorial-module {
                background-color: #1a1a1a;
                border-left-color: #6c757d;
            }
            .tutorial-module h3 {
                color: #0d6efd;
                margin-bottom: 1rem;
            }
            body.dark-theme .tutorial-module h3 {
                color: #adb5bd;
            }
            .tutorial-module p {
                line-height: 1.6;
                margin-bottom: 1rem;
            }
            .tutorial-module ul {
                margin-left: 1.2rem;
                margin-bottom: 1rem;
            }
            .tutorial-module li {
                margin-bottom: 0.5rem;
            }
            .tutorial-plot-container {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 1rem;
                margin: 1rem 0;
            }
            body.dark-theme .tutorial-plot-container {
                background-color: #000000;
                border-color: #444;
            }
            .tutorial-intro {
                background-color: #e3f2fd;
                border-radius: 8px;
                padding: 2rem;
                margin-bottom: 2rem;
                border-left: 4px solid #2196f3;
            }
            body.dark-theme .tutorial-intro {
                background-color: #0d1b2a;
                border-left-color: #415a77;
            }
            
            /* Dark mode refinements */
            body.dark-theme {
                background-color: #000000;
                color: #ffffff;
            }
            body.dark-theme footer {
                background-color: #000000;
                color: #ffffff;
            }
            body.dark-theme .nav-tabs .nav-link {
                color: #ffffff;
            }
            body.dark-theme .nav-tabs .nav-link.active {
                color: #0d6efd;
            }
            body.dark-theme input[type="file"],
            body.dark-theme .btn,
            body.dark-theme select,
            body.dark-theme option {
                color: #ffffff;
                background-color: #333333;
            }
            body.dark-theme .main-content {
                background-color: #000000 !important;
            }
            body.dark-theme .dropdown-menu {
                background-color: #000000 !important;
                color: #ffffff !important;
                border: 1px solid #444444 !important;
            }
            body.dark-theme .dropdown-menu .dropdown-item {
                color: #ffffff !important;
            }
            body.dark-theme .dropdown-menu .dropdown-item:hover,
            body.dark-theme .dropdown-menu .dropdown-item.active,
            body.dark-theme .dropdown-menu .dropdown-item:focus {
                background-color: #222222 !important;
                color: #ffffff !important;
            }
            """
        ),
        ui.tags.script(
            """
            Shiny.addCustomMessageHandler("update_theme", function(theme) {
                document.body.classList.toggle("dark-theme", theme === "Dark");
                document.body.classList.toggle("light-theme", theme === "Light");
                
                // Swap logo based on theme
                var logo = document.getElementById('maidr_logo');
                if (logo) {
                    logo.src = (theme === "Dark") ? "img/dark.png" : "img/light.jpg";
                }
                // Announce theme change
                var announcement = "Theme changed to " + theme + " mode";
                announceToScreenReader(announcement);
            });
            
            Shiny.addCustomMessageHandler("announce", function(message) {
                announceToScreenReader(message);
            });
            
            Shiny.addCustomMessageHandler("show_help", function(message) {
                Shiny.setInputValue("show_help_modal", Math.random());
            });
            
            Shiny.addCustomMessageHandler("download_file", function(data) {
                console.log('Download triggered for:', data.filename);
                
                try {
                    var mimeType = data.mime_type || 'text/html;charset=utf-8';
                    var blob = new Blob([data.content], { type: mimeType });
                    console.log('Blob created:', blob.size, 'bytes');
                    
                    if (typeof document.createElement('a').download !== 'undefined') {
                        console.log('Using download attribute method');
                        
                        var link = document.createElement('a');
                        var url = window.URL.createObjectURL(blob);
                        link.href = url;
                        link.download = data.filename;
                        link.style.display = 'none';
                        
                        document.body.appendChild(link);
                        console.log('Link added to document');
                        
                        link.click();
                        console.log('Link clicked');
                        
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
                        var url = window.URL.createObjectURL(blob);
                        var newWindow = window.open(url, '_blank');
                        if (!newWindow) {
                            console.log('Popup blocked, trying alternative');
                            window.location.href = url;
                        }
                        setTimeout(function() {
                            window.URL.revokeObjectURL(url);
                        }, 1000);
                    }
                    
                    announceToScreenReader('Download started: ' + data.filename);
                    
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
                
                ariaLive.textContent = '';
                setTimeout(function() {
                    ariaLive.textContent = message;
                }, 100);
            }
            
            // Announce when plots are loaded
            document.addEventListener('DOMContentLoaded', function() {
                var observer = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                            for (var i = 0; i < mutation.addedNodes.length; i++) {
                                var node = mutation.addedNodes[i];
                                if (node.nodeType === 1) {
                                    if (node.querySelector && node.querySelector('svg, canvas, img')) {
                                        announceToScreenReader('Plot has been updated and is now available for exploration');
                                        break;
                                    }
                                }
                            }
                        }
                    });
                });
                
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
                    
                    if (event.key === 'h' || event.key === 'H') {
                        if (!isInputField) {
                            event.preventDefault();
                            
                            var helpModal = document.querySelector('#help_modal');
                            var isModalOpen = helpModal && helpModal.style.display !== 'none' && 
                                            helpModal.classList.contains('show');
                            
                            if (isModalOpen) {
                                Shiny.setInputValue("close_help", Math.random());
                                announceToScreenReader('Help menu closed.');
                            } else {
                                Shiny.setInputValue("show_help_modal", Math.random());
                                announceToScreenReader('Help menu opened. Use Tab to navigate through help sections.');
                            }
                        }
                    }
                    
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

            Shiny.addCustomMessageHandler("show_alert", function(data) {
                try {
                    var alertDiv = document.createElement('div');
                    var alertType = data.type || 'info';
                    alertDiv.className = 'alert alert-' + alertType + ' alert-dismissible fade show';
                    alertDiv.setAttribute('role', 'alert');
                    alertDiv.style.position = 'fixed';
                    alertDiv.style.top = '20px';
                    alertDiv.style.right = '20px';
                    alertDiv.style.zIndex = 2000;
                    alertDiv.textContent = data.message || 'Notification';

                    var closeBtn = document.createElement('button');
                    closeBtn.type = 'button';
                    closeBtn.className = 'btn-close';
                    closeBtn.setAttribute('aria-label', 'Close');
                    closeBtn.addEventListener('click', function() { alertDiv.remove(); });
                    alertDiv.appendChild(closeBtn);

                    document.body.appendChild(alertDiv);
                    setTimeout(function(){ try{alertDiv.classList.remove('show'); alertDiv.remove();}catch(e){} }, 4000);
                } catch(e) {
                    console.error('show_alert handler failed', e);
                }
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
    # Main content
    ui.tags.main(
        {"role": "main", "aria-label": "Main content"},
        ui.div(
            ui.navset_tab(
                # About tab with logo
                ui.nav_panel(
                    ui.tags.img(src="img/light.jpg", id="maidr_logo", alt="About Us", style="height:30px;"),
                    ui.div(
                        ui.tags.img(src="img/lab_logo.jpg", alt="(x)Ability Design Lab Logo", class_="about-logo"),
                        ui.div(
                            ui.h2("MAIDR Finance Dashboard", class_="mb-3 fw-bold"),
                            ui.p(
                                "Welcome to the MAIDR Finance Dashboard, a specialized tool for learning financial chart interpretation through accessible, multimodal data visualization. This dashboard focuses specifically on candlestick charts - the fundamental building blocks of financial analysis.",
                                class_="about-paragraph"
                            ),
                            ui.p(
                                "Developed by the ",
                                ui.tags.a("(x)Ability Design Lab", href="https://xabilitylab.ischool.illinois.edu/", target="_blank"),
                                " at the University of Illinois Urbana–Champaign, this dashboard provides synchronized visual, tactile (braille), textual, and sonic representations of financial data, making trading education accessible to all users.",
                                class_="about-paragraph"
                            ),
                            ui.tags.ul(
                                ui.tags.li("Interactive candlestick charts with three layers: price candles, volume bars, and moving average trend lines"),
                                ui.tags.li("Structured tutorial covering fundamental concepts from basic patterns to advanced trading strategies"),
                                ui.tags.li("Hands-on practice environment with real-time chart generation"),
                                ui.tags.li("Screen reader compatible with full keyboard navigation support"),
                                ui.tags.li("Downloadable charts in both SVG and HTML formats for further study"),
                                class_="mb-3"
                            ),
                            ui.p(
                                "Navigate through the tutorial to learn essential concepts like bullish/bearish patterns, trend analysis, and reversal strategies. Then apply your knowledge in the practice section with interactive chart generation.",
                                class_="about-paragraph"
                            ),
                            class_="about-text"
                        ),
                        class_="about-section my-4"
                    )
                ),
                # Settings dropdown
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
                # Tutorial tab
                ui.nav_panel(
                    "Tutorial",
                    ui.div(
                        ui.div(
                            ui.h1("Tutorial: Interpreting Financial Charts for Trading", class_="text-center mb-4"),
                            ui.p(
                                "Welcome to this introductory guide to understanding financial charts. This session is specifically designed for blind and visually impaired users, working with charts that have three layers of information, all readable by screen-reading software:",
                                class_="lead text-center"
                            ),
                            ui.tags.ol(
                                ui.tags.li("Candlesticks: Represent price movements over a specific period"),
                                ui.tags.li("Volume Bars: Show trading activity for each period"),
                                ui.tags.li("Moving Average Trend Line: Helps identify overall market direction"),
                                class_="mb-4"
                            ),
                            ui.p(
                                "In the MAIDR Finance Dashboard, you can navigate between these layers using Page Up and Page Down keys. Our goal is to help you build a mental model of market behavior to identify potential trading opportunities.",
                                class_="text-center mb-4"
                            ),
                            class_="tutorial-intro"
                        ),
                        
                        # Module 1: Understanding the Building Blocks
                        ui.div(
                            ui.h3("Module 1: Understanding the Building Blocks"),
                            ui.p(
                                "Let's start with the most fundamental component: a single candlestick. Each candlestick tells the trading story for one period and provides four key pieces of information:"
                            ),
                            ui.tags.ul(
                                ui.tags.li("Open: The price at the beginning of the period"),
                                ui.tags.li("Close: The price at the end of the period"),
                                ui.tags.li("High: The highest price reached during the period"),
                                ui.tags.li("Low: The lowest price reached during the period")
                            ),
                            ui.p(
                                "The relationship between open and close prices determines who was in control - buyers or sellers. This leads to two key concepts:"
                            ),
                            ui.tags.ul(
                                ui.tags.li("Bullish candle: Close price is higher than open price (buyers in control)"),
                                ui.tags.li("Bearish candle: Close price is lower than open price (sellers in control)")
                            ),
                            ui.div(
                                ui.h4("Explore Basic Candlestick Patterns"),
                                ui.p("The chart below shows clear examples of bullish and bearish candles. Use your screen reader to explore each candle's open, high, low, and close values."),
                                ui.output_ui("tutorial_basics_output"),
                                class_="tutorial-plot-container"
                            ),
                            class_="tutorial-module"
                        ),
                        
                        # Module 2: Reading the Market's Story
                        ui.div(
                            ui.h3("Module 2: Reading the Market's Story"),
                            ui.p("Now let's understand how multiple candlesticks tell the market's story through trends and volatility:"),
                            ui.tags.ul(
                                ui.tags.li("Uptrend: Series of higher highs and higher lows (bullish sign)"),
                                ui.tags.li("Downtrend: Series of lower highs and lower lows (bearish sign)"),
                                ui.tags.li("Volatility: Measured by the difference between high and low prices"),
                                ui.tags.li("Consolidation: Sideways trading showing market indecision"),
                                ui.tags.li("Momentum: Strong, sustained price movement in one direction")
                            ),
                            ui.p(
                                "Pay attention to price gaps - when the opening price differs significantly from the previous close, often signaling strong shifts in market sentiment."
                            ),
                            ui.div(
                                ui.h4("Explore Market Trends and Volatility"),
                                ui.p("This chart demonstrates an uptrend, followed by a downtrend, and then high volatility. Notice how the moving average lines help identify the overall direction."),
                                ui.output_ui("tutorial_trends_output"),
                                class_="tutorial-plot-container"
                            ),
                            class_="tutorial-module"
                        ),
                        
                        # Module 3: Basic Trading Concepts
                        ui.div(
                            ui.h3("Module 3: Basic Trading Concepts"),
                            ui.p("Understanding key trading concepts helps identify potential opportunities:"),
                            ui.tags.ul(
                                ui.tags.li("Reversal: Change in price trend direction"),
                                ui.tags.li("Breakout: Price moves beyond known support or resistance levels"),
                                ui.tags.li("Entry Point: Price level where you enter a trade"),
                                ui.tags.li("Stop-Loss: Pre-set order to limit losses if price moves against you"),
                                ui.tags.li("Take-Profit: Order to close trade once profit target is reached")
                            ),
                            ui.p(
                                "Combining analysis of candlesticks, volume, and trend lines helps identify logical entry points and set appropriate stop-loss and take-profit targets."
                            ),
                            ui.div(
                                ui.h4("Explore Reversal and Breakout Patterns"),
                                ui.p("This chart shows a downtrend, followed by a reversal formation, and then a breakout upward. Notice the volume increase during these key moments."),
                                ui.output_ui("tutorial_reversal_output"),
                                class_="tutorial-plot-container"
                            ),
                            class_="tutorial-module"
                        ),
                        
                        # Module 4: Basic Trading Strategies
                        ui.div(
                            ui.h3("Module 4: Basic Trading Strategies"),
                            ui.p("Here are two fundamental candlestick patterns used in trading strategies:"),
                            
                            ui.h4("Strategy 1: The Bullish Hammer Reversal"),
                            ui.p("Used when a market has been in a downtrend and a 'Hammer' pattern appears:"),
                            ui.tags.ul(
                                ui.tags.li("Market Context: Must follow a downtrend"),
                                ui.tags.li("Pattern: Small body near top, very long lower wick, little/no upper wick"),
                                ui.tags.li("Signal: Lower wick should be at least twice the body length"),
                                ui.tags.li("Entry: Wait for confirmation on the next candle"),
                                ui.tags.li("Stop-Loss: Place just below the hammer's low")
                            ),
                            ui.div(
                                ui.h5("Explore Hammer Reversal Pattern"),
                                ui.p("This chart shows a downtrend leading to a hammer formation on day 7, followed by confirmation and recovery."),
                                ui.output_ui("tutorial_hammer_output"),
                                class_="tutorial-plot-container"
                            ),
                            
                            ui.h4("Strategy 2: The Bearish Shooting Star Reversal"),
                            ui.p("Used when a market has been in an uptrend and a 'Shooting Star' pattern appears:"),
                            ui.tags.ul(
                                ui.tags.li("Market Context: Must follow an uptrend"),
                                ui.tags.li("Pattern: Small body at bottom, long upper wick, very small lower wick"),
                                ui.tags.li("Signal: Indicates selling pressure after buyers tried to push higher"),
                                ui.tags.li("Entry: Wait for confirmation on the next candle"),
                                ui.tags.li("Stop-Loss: Place just above the shooting star's high")
                            ),
                            ui.div(
                                ui.h5("Explore Shooting Star Reversal Pattern"),
                                ui.p("This chart shows an uptrend leading to a shooting star formation on day 7, followed by confirmation and decline."),
                                ui.output_ui("tutorial_shooting_star_output"),
                                class_="tutorial-plot-container"
                            ),
                            
                            ui.p(
                                "Remember: These patterns require confirmation on the following candle before entering a trade. Always use proper risk management with stop-loss orders.",
                                class_="alert alert-info"
                            ),
                            class_="tutorial-module"
                        ),
                        
                        class_="tutorial-content"
                    )
                ),
                # Tasks tab
                ui.nav_panel(
                    "Practice Tasks",
                    ui.div(
                        ui.h2("Practice Your Skills", class_="text-center mb-4"),
                        ui.p(
                            "Now it's time to apply what you've learned! Use the controls below to generate different candlestick charts and practice identifying patterns, trends, and trading opportunities.",
                            class_="lead text-center mb-4"
                        ),
                        ui.row(
                            ui.column(
                                3,
                                ui.div(
                                    ui.h4("Chart Controls"),
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
                                    ui.br(),
                                    ui.div(
                                        ui.input_action_button(
                                            "download_graphics_candlestick",
                                            "Download SVG",
                                            class_="btn btn-primary btn-sm",
                                        ),
                                        ui.input_action_button(
                                            "download_html_candlestick",
                                            "Download HTML",
                                            class_="btn btn-secondary btn-sm",
                                        ),
                                        ui.input_action_button(
                                            "embed_code_button_candlestick",
                                            "Embed Code",
                                            class_="btn btn-success btn-sm",
                                            aria_label="Get embed code for your website",
                                        ),
                                        class_="d-grid gap-2",
                                    ),
                                    class_="card p-3"
                                )
                            ),
                            ui.column(
                                9,
                                ui.div(
                                    ui.h4("Interactive Candlestick Chart"),
                                    ui.p(
                                        "This chart includes all three layers: candlesticks, volume bars, and moving average trend lines. Use Page Up/Down to navigate between layers in your screen reader.",
                                        class_="text-muted"
                                    ),
                                    ui.output_ui("create_candlestick_output"),
                                    class_="card p-3"
                                )
                            )
                        )
                    )
                ),
            ),
            class_="main-content"
        ),
    ),
    # Footer
    ui.tags.footer(
        ui.div(
            ui.p("© 2025 (x)Ability Design Lab. All rights reserved.", class_="mb-1"),
            ui.p("MAIDR Finance Dashboard - Making Financial Data Accessible", class_="small mb-0"),
            class_="text-center"
        ),
        class_="app-footer"
    ),
)

# Define the server logic
def server(input, output, session):
    # Reactive value to store the current figure
    current_figure = reactive.Value(None)

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

    # Tutorial plot outputs
    @output
    @render_maidr
    def tutorial_basics_output():
        """Create basic candlestick tutorial plot"""
        try:
            ax = create_tutorial_candlestick_basics(input.theme())
            if ax is not None:
                current_figure.set(ax.figure)
                return ax
        except Exception as e:
            print(f"Error creating tutorial basics: {e}")
            return None

    @output
    @render_maidr
    def tutorial_trends_output():
        """Create trends and volatility tutorial plot"""
        try:
            ax = create_tutorial_trends_volatility(input.theme())
            if ax is not None:
                current_figure.set(ax.figure)
                return ax
        except Exception as e:
            print(f"Error creating tutorial trends: {e}")
            return None

    @output
    @render_maidr
    def tutorial_reversal_output():
        """Create reversal and breakout tutorial plot"""
        try:
            ax = create_tutorial_reversal_breakout(input.theme())
            if ax is not None:
                current_figure.set(ax.figure)
                return ax
        except Exception as e:
            print(f"Error creating tutorial reversal: {e}")
            return None

    @output
    @render_maidr
    def tutorial_hammer_output():
        """Create hammer pattern tutorial plot"""
        try:
            ax = create_tutorial_hammer_pattern(input.theme())
            if ax is not None:
                current_figure.set(ax.figure)
                return ax
        except Exception as e:
            print(f"Error creating tutorial hammer: {e}")
            return None

    @output
    @render_maidr
    def tutorial_shooting_star_output():
        """Create shooting star pattern tutorial plot"""
        try:
            ax = create_tutorial_shooting_star_pattern(input.theme())
            if ax is not None:
                current_figure.set(ax.figure)
                return ax
        except Exception as e:
            print(f"Error creating tutorial shooting star: {e}")
            return None

    # Main candlestick chart for practice
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

    # Generic function to handle embed code generation
    async def handle_embed_code_generation():
        """Generate embed code with full HTML content that preserves MAIDR functionality"""
        try:
            # Get the current figure
            fig = current_figure.get()
            if fig is None:
                fig = plt.gcf()
            
            if not fig or not fig.get_axes():
                await announce_to_screen_reader("No plot available to generate embed code")
                await session.send_custom_message("show_alert", {"type":"warning", "message":"No plot available. Please generate a plot before creating embed code."})
                return
            
            # Generate HTML content using the same logic as download
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
                
                # Extract only the inner content for embedding
                embed_code = extract_embed_content(html_content)
                
                print(f"Generated embed code length: {len(embed_code)}")
                
                # Send the embed code to client side
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

    # Handle embed code button click
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

    # Generic function to create HTML content and trigger download
    async def trigger_html_download():
        """Generate HTML content and trigger browser download with save dialog"""
        try:
            # Get the current figure
            fig = current_figure.get()
            if fig is None:
                fig = plt.gcf()
            
            if not fig or not fig.get_axes():
                await announce_to_screen_reader("No plot available to download")
                await session.send_custom_message("show_alert", {"type":"warning", "message":"No plot available. Please generate a plot before creating embed code."})
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
                company = input.candlestick_company()
                timeframe = input.candlestick_timeframe()
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{company}_{timeframe}_candlestick_{timestamp}.html"
                
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

    # Handle download button click
    @reactive.effect
    @reactive.event(input.download_html_candlestick)
    async def download_html_candlestick_clicked():
        await trigger_html_download()

    # Generic SVG download handler
    async def trigger_svg_download():
        """Generate SVG in-memory and send to browser for download."""
        try:
            fig = current_figure.get()
            if fig is None:
                fig = plt.gcf()
            if not fig or not fig.get_axes():
                await announce_to_screen_reader("No plot available to download")
                await session.send_custom_message("show_alert", {"type":"warning", "message":"No plot available. Please generate a plot before creating embed code."})
                return

            import io
            buffer = io.StringIO()
            fig.savefig(buffer, format='svg', bbox_inches='tight')
            svg_content = buffer.getvalue()
            buffer.close()

            # Generate filename
            company = input.candlestick_company()
            timeframe = input.candlestick_timeframe()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{company}_{timeframe}_candlestick_{timestamp}.svg"

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

    # Download Graphics button event
    @reactive.effect
    @reactive.event(input.download_graphics_candlestick)
    async def download_graphics_candlestick_clicked():
        await trigger_svg_download()

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
        div_match = re.search(r'(<div[^>]*>.*?<link.*?maidr.*?<script.*?</script>.*?<div.*?</div>\s*</div>)', html_content, re.DOTALL | re.IGNORECASE)
        
        if div_match:
            body_content = div_match.group(1).strip()
        else:
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
    iframe_embed = f'''<iframe 
    srcdoc="{escaped_html}"
    style="width: 100%; height: 600px; border: 1px solid #ccc; border-radius: 4px;"
    sandbox="allow-scripts allow-same-origin"
    title="Accessible Interactive Candlestick Chart with MAIDR">
</iframe>'''
    
    return iframe_embed

# Create the Shiny app
static_img_dir = Path(__file__).parent / "img"
app = App(app_ui, server, static_assets={"/img": static_img_dir})