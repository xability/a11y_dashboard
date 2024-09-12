import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import maidr

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

# Apply global CSS for Light and Dark themes
def apply_global_theme(theme):
    if theme == "Dark":
        st.markdown(
            """
            <style>
            body {
                background-color: #2E2E2E;
                color: white;
            }
            .stTabs [role="tab"] {
                background-color: #444444;
                color: white;
            }
            .stTabs [role="tablist"] {
                border-bottom: 1px solid white;
            }
            </style>
            """, unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            body {
                background-color: white;
                color: black;
            }
            .stTabs [role="tab"] {
                background-color: #f0f0f0;
                color: black;
            }
            .stTabs [role="tablist"] {
                border-bottom: 1px solid black;
            }
            </style>
            """, unsafe_allow_html=True
        )

# Set up the Streamlit app
st.header("Streamlit App with Maidr Integration: Plot Tutorials")

# Global theme toggle (Light/Dark)
theme = st.radio("Select theme:", ["Light", "Dark"])
apply_global_theme(theme)

# Sidebar for plot size control
st.sidebar.header("Figure Size Control")

# Slider to adjust figure size dynamically
fig_width = st.sidebar.slider("Figure width", min_value=5, max_value=15, value=10)
fig_height = st.sidebar.slider("Figure height", min_value=5, max_value=12, value=7)  # Default height set to 7

# Tabs for different plots
tab1, tab2, tab3 = st.tabs(["Histogram", "Box Plot", "Scatter Plot"])

# Define a function to set the plot theme based on user selection
def set_theme(fig, ax, theme):
    if theme == "Dark":
        plt.style.use('dark_background')
        fig.patch.set_facecolor('#2E2E2E')
        ax.set_facecolor('#2E2E2E')
    else:
        plt.style.use('default')
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')

# Histogram Tab
with tab1:
    st.subheader("Histogram")
    
    # Dropdowns for histogram selection
    distribution_type = st.selectbox(
        "Select histogram distribution type:",
        ["Normal Distribution", "Positively Skewed", "Negatively Skewed",
         "Unimodal Distribution", "Bimodal Distribution", "Multimodal Distribution"]
    )
    hist_color = st.selectbox(
        "Select histogram color:",
        list(color_palettes.keys())
    )
    
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

    # Create histogram plot
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))  # Dynamically sized figure with default height 7
    set_theme(fig, ax, theme)
    sns.histplot(data, kde=True, bins=20, color=color_palettes[hist_color], edgecolor="white", ax=ax)
    ax.set_title(f"Histogram: {distribution_type}")
    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")
    
    # Render the plot using Maidr
    st.components.v1.html(maidr.render(ax).get_html_string(), height=fig_height * 100, width=fig_width * 100)  # Dynamic height and width

# Box Plot Tab
with tab2:
    st.subheader("Box Plot")
    
    # Dropdowns for box plot selection
    boxplot_type = st.selectbox(
        "Select box plot type:",
        ["Positively Skewed with Outliers", "Negatively Skewed with Outliers",
         "Symmetric with Outliers", "Symmetric without Outliers"]
    )
    boxplot_color = st.selectbox(
        "Select box plot color:",
        list(color_palettes.keys())
    )
    
    # Generate data based on the selected box plot type
    if boxplot_type == "Positively Skewed with Outliers":
        data = np.random.lognormal(mean=0, sigma=0.5, size=1000)
    elif boxplot_type == "Negatively Skewed with Outliers":
        data = -np.random.lognormal(mean=0, sigma=0.5, size=1000)
    elif boxplot_type == "Symmetric with Outliers":
        data = np.random.normal(loc=0, scale=1, size=1000)
    elif boxplot_type == "Symmetric without Outliers":
        # Ensure no outliers by limiting the range of data
        data = np.random.normal(loc=0, scale=1, size=1000)
        data = data[(data > -1.5) & (data < 1.5)]  # Limit to ensure no outliers

    # Create box plot
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))  # Dynamically sized figure with default height 7
    set_theme(fig, ax, theme)
    sns.boxplot(x=data, ax=ax, color=color_palettes[boxplot_color])
    ax.set_title(f"Box Plot: {boxplot_type}")
    ax.set_xlabel("Value")
    
    # Render the plot using Maidr
    st.components.v1.html(maidr.render(ax).get_html_string(), height=fig_height * 100, width=fig_width * 100)  # Dynamic height and width

# Scatter Plot Tab
with tab3:
    st.subheader("Scatter Plot")
    
    # Dropdowns for scatter plot selection
    scatterplot_type = st.selectbox(
        "Select scatter plot type:",
        ["No Correlation", "Weak Positive Correlation", "Strong Positive Correlation",
         "Weak Negative Correlation", "Strong Negative Correlation"]
    )
    scatter_color = st.selectbox(
        "Select scatter plot color:",
        list(color_palettes.keys())
    )
    
    # Generate data based on the selected correlation type
    num_points = np.random.randint(20, 31)
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

    # Create scatter plot
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))  # Dynamically sized figure with default height 7
    set_theme(fig, ax, theme)
    sns.scatterplot(x=x, y=y, ax=ax, color=color_palettes[scatter_color])
    ax.set_title(f"Scatter Plot: {scatterplot_type}")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    
    # Render the plot using Maidr
    st.components.v1.html(maidr.render(ax).get_html_string(), height=fig_height * 100, width=fig_width * 100)  # Dynamic height and width