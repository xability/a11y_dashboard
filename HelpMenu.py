"""
Help Menu Module for A11Y Dashboard

This module provides comprehensive help content for users to understand
how to use the accessibility dashboard effectively.
"""

from shiny import ui

def get_help_content():
    """
    Returns the complete help content as a UI element
    """
    return ui.div(
        ui.h2("A11Y Dashboard Help Guide", class_="text-center mb-4"),
        
        # Quick Start Section
        ui.div(
            ui.h3("Quick Start"),
            ui.p("Create accessible data visualizations with screen reader support and MAIDR integration. Press 'h' to toggle help or ESC to close."),
            ui.p(ui.strong("Navigation: "), "Tab between elements, Enter/Space to activate, themes in Settings menu."),
            class_="mb-4"
        ),
        
        # CSV Data Structure Section
        ui.div(
            ui.h3("CSV Data Requirements"),
            ui.p("Standard CSV files with headers in first row. Numeric columns for quantities, text for categories. Use empty cells for missing data."),
            ui.pre(
                """Name,Age,Department,Salary
John,28,Engineering,75000
Sarah,35,Marketing,68000""",
                class_="bg-light p-2 border rounded small"
            ),
            class_="mb-4"
        ),
        
        # Dashboard Features Section
        ui.div(
            ui.h3("Plot Types & Custom Creation"),
            ui.p(ui.strong("Available plots: "), "Histogram, Box Plot, Scatter Plot, Bar Plot, Line Plot, Heatmap, Multiline, Multilayer, Multipanel, Candlestick"),
            ui.p(ui.strong("Custom workflow: "), "Upload CSV → Select plot type → Choose variables → Customize colors → Generate accessible plot"),
            class_="mb-4"
        ),
        
        # Variable Requirements Section
        ui.div(
            ui.h3("Variable Requirements"),
            ui.p("Histogram: 1 numeric | Box Plot: 1 numeric + optional categorical | Scatter/Line: 2 numeric | Bar: 1 categorical | Heatmap: 2 categorical + 1 numeric | Multiline: 2 numeric + 1 categorical"),
            class_="mb-4"
        ),
        
        # Saving & Accessibility Section
        ui.div(
            ui.h3("Saving & Accessibility"),
            ui.p(ui.strong("Save options: "), "SVG for publications, HTML for accessible version with MAIDR integration"),
            ui.p(ui.strong("Accessibility: "), "Full keyboard navigation, screen reader support, audio descriptions, dark theme, ARIA announcements"),
            class_="mb-4"
        ),
        
        # Troubleshooting Section
        ui.div(
            ui.h3("Troubleshooting"),
            ui.p("Plot issues: check variable selection and CSV format. Save issues: generate plot first. Accessibility: try refresh or theme switch."),
            class_="mb-4"
        ),
        
        # Keyboard Shortcuts Section
        ui.div(
            ui.h3("Keyboard Shortcuts"),
            ui.tags.ul(
                ui.tags.li(ui.strong("h: "), "Toggle this help menu"),
                ui.tags.li(ui.strong("ESC: "), "Close this help menu"),
                ui.tags.li(ui.strong("Tab: "), "Navigate between elements"),
                ui.tags.li(ui.strong("Enter/Space: "), "Activate buttons"),
                ui.tags.li(ui.strong("Arrow Keys: "), "Navigate dropdowns")
            ),
            class_="mb-4"
        ),
        
        # Footer
        ui.div(
            ui.hr(),
            ui.p(ui.strong("Press ESC to close"), class_="text-center")
        ),
        
        class_="help-content p-4",
        style="max-height: 80vh; overflow-y: auto; background-color: var(--bs-light); border-radius: 8px;"
    )

def get_help_modal():
    """
    Returns a modal dialog containing the help content
    """
    return ui.modal(
        get_help_content(),
        id="help_modal",
        size="xl",
        easy_close=True,
        footer=ui.div(
            ui.input_action_button(
                "close_help", 
                "Close Help (or press 'h')", 
                class_="btn btn-secondary"
            ),
            class_="text-center"
        )
    )

# Help content for quick reference tooltips
QUICK_HELP_TIPS = {
    "csv_upload": "Upload a CSV file with headers in the first row. Numeric columns for quantities, text columns for categories.",
    "plot_type": "Choose the type of visualization based on your data and analysis needs.",
    "variables": "Select appropriate variables based on the plot requirements shown in the help menu.",
    "colors": "Choose color schemes that work well for your audience and accessibility needs.",
    "save_svg": "Save a scalable vector image perfect for presentations and publications.",
    "save_html": "Save an accessible web version that works with screen readers and assistive technology.",
    "theme": "Switch between light and dark themes for better visibility.",
    "maidr": "MAIDR provides audio descriptions and sonification for accessible data exploration."
} 