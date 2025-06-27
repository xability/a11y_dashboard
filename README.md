# Accessibility Dashboard for Data Visualization

## Live Dashboard Access

The accessibility dashboard is available at the following endpoints:

- **Primary**: https://xabilitylab.shinyapps.io/a11y_dashboard/
- **Backup**: https://xabilitylab.ischool.illinois.edu/a11y_dashboard/

Both endpoints are identical from a user’s perspective; the difference lies in how they’re hosted:

Primary endpoint runs on a remote Python-backed Shiny server (shinyapps.io), offering fast, automatically scaled performance.

Backup endpoint is delivered as a static WebAssembly bundle via Shinylive; everything runs in your browser using Pyodide, with no server backend—may feel slightly slower on older or less powerful machines.

## Dashboard Features

### Overview
This interactive dashboard provides accessible data visualization tools that generate plots with MAIDR (Multimodal Access and Interactive Data Representation) support, making visualizations accessible to users with visual impairments through screen readers and sonification.

### Dashboard Tabs

#### 1. Settings
- **Theme Selection**: Switch between Light and Dark themes for better visual accessibility
- **Save HTML**: Export accessible HTML versions of plots with embedded MAIDR functionality

#### 2. Create your own Custom Plot
Upload your own CSV data and create custom visualizations:
- **File Upload**: Upload CSV files to analyze your own data
- **Data Type Detection**: Automatic identification of numeric and categorical variables
- **Plot Type Selection**: Choose from 10 different plot types
- **Color Customization**: Select from multiple color palettes
- **Variable Selection**: Dynamic dropdowns for selecting appropriate variables based on plot type
- **SVG Export**: Save plots as SVG files to Downloads folder

#### 3. Histogram
Generate histogram visualizations with options for:
- **Distribution Types**: Normal, Positively Skewed, Negatively Skewed, Unimodal, Bimodal, Multimodal
- **Color Options**: Default, Red, Green, Blue, Purple, Orange

#### 4. Box Plot
Create box plots with various configurations:
- **Plot Types**: Positively Skewed with Outliers, Negatively Skewed with Outliers, Symmetric with/without Outliers
- **Color Customization**: Multiple color palette options

#### 5. Scatter Plot
Generate scatter plots showing different correlation patterns:
- **Correlation Types**: No Correlation, Weak/Strong Positive/Negative Correlation
- **Color Themes**: Customizable color palettes

#### 6. Bar Plot
Create categorical data visualizations:
- **Color Options**: Multiple color palette choices
- **Automatic Data Generation**: Uses predefined categorical data for demonstration

#### 7. Line Plot
Generate time series and trend visualizations:
- **Pattern Types**: Linear Trend, Exponential Growth, Sinusoidal Pattern, Random Walk
- **Color Customization**: Various color options

#### 8. Heatmap
Create correlation and intensity visualizations:
- **Heatmap Types**: Random data, Correlated data, Checkerboard patterns
- **Built-in Color Scales**: Optimized for accessibility

#### 9. Multiline Plot
Generate multiple line series on a single plot:
- **Series Types**: Simple Trends, Seasonal Patterns, Growth Comparison, Random Series
- **Color Palettes**: Default, Colorful, Pastel, Dark Tones, Paired Colors, Rainbow

#### 10. Multilayer Plot
Combine different plot types in layers:
- **Background Plot Types**: Bar Plot, Histogram, Scatter Plot
- **Overlay Options**: Line plots over background visualizations
- **Dual Color Control**: Separate color selection for background and overlay elements

#### 11. Multipanel Plot
Create complex multi-subplot visualizations:
- **Layout**: Three-panel plots combining different visualization types
- **Automatic Configuration**: Pre-configured line and bar plot combinations

#### 12. Candlestick Chart
Financial data visualization tool:
- **Companies**: Tesla, Apple, NVIDIA, Microsoft, Google, Amazon
- **Timeframes**: Daily, Monthly, Yearly data views
- **Financial Metrics**: Open, High, Low, Close price visualization

### Accessibility Features
- **MAIDR Integration**: All plots include Multimodal Access and Interactive Data Representation
- **Screen Reader Support**: Compatible with assistive technologies
- **Keyboard Navigation**: Full keyboard accessibility
- **Theme Options**: Light and dark themes for visual accessibility
- **Export Options**: HTML and SVG export capabilities

# Running the Shiny App Locally

This guide will walk you through setting up and running the Shiny app using Python, based on the structure of your directory.

### Prerequisites
1. **Python 3.7+**: Ensure you have Python installed. You can check this by running:
   ```bash
   python --version
   ```
   If you don't have it installed, download Python [here](https://www.python.org/downloads/).

2. **Shiny for Python**: You will need to install `shiny`, which is Posit's package for Python.

3. **Virtual Environment (optional but recommended)**: Using a virtual environment is a good practice to isolate dependencies.

### Steps to Run the App

#### 1. Clone or Navigate to the Directory
First, make sure you are in the directory containing the app files. If you need to clone a GitHub repository, use:
```bash
git clone <repository-url>
cd <repository-folder>
```

#### 2. Set up a Virtual Environment (Optional)
To avoid dependency conflicts, set up a virtual environment in the directory. 

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

#### 3. Install Dependencies
Install `shiny` and other necessary dependencies specified in the `requirements.txt` file.

1. **Install `shiny`**:
   ```bash
   pip install shiny
   ```

2. **Install the other dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

#### 4. Run the App
Once all dependencies are installed, you can run the Shiny app.

1. Run the app:
   ```bash
   shiny run --reload app.py
   ```

   The `--reload` option allows for automatic reloading of the app if you make any code changes.

2. After running the command, you should see output like:
   ```bash
   Listening on http://127.0.0.1:8000
   ```

3. Open the provided URL (`http://127.0.0.1:8000`) in your browser to access the Shiny app.

### Additional Notes:
- **Dummy Data**: The file `dummy_data_for_practice.csv` is included for you to test the app's functionality with dummy data. Please free to use your own data!
- **VS Code Configuration**: If you use VS Code, you may want to install the `Shiny for Python` extension, which will help you run the app and display the content in an in-window browser.

## Running the Shiny App in the Browser with Shinylive (Pyodide)

You can run this Shiny for Python app entirely in your browser using [Shinylive](https://shinylive.io/py), which uses Pyodide to run Python code client-side (no server needed).

### Steps to Export and Run with Shinylive

1. **Install Shinylive CLI** (if not already installed):
   ```bash
   pip install shinylive
   ```

2. **Export your app for Shinylive:**
   ```bash
   shinylive export . output_dir
   ```
   This will create an `output_dir` folder with all the files needed to run your app in the browser.

3. **Serve the exported app with a local HTTP server:**
   ```bash
   python3 -m http.server --directory output_dir 8008
   ```
   Then open [http://localhost:8008](http://localhost:8008) in your browser.

   > **Note:** Opening `index.html` directly (with `file://`) will NOT work due to browser security restrictions. Always use a local HTTP server.

### What is Shinylive/Pyodide?
- **Shinylive** lets you run Shiny for Python apps in the browser using **Pyodide** (Python compiled to WebAssembly).
- All computation happens client-side; no server is required after export.
