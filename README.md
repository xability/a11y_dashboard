# Running the Shiny App Locally

This guide will walk you through setting up and running the Shiny app using Python, based on the structure of your directory.

### Prerequisites
1. **Python 3.7+**: Ensure you have Python installed. You can check this by running:
   ```bash
   python --version
   ```
   If you don’t have it installed, download Python [here](https://www.python.org/downloads/).

2. **Shiny for Python**: You will need to install `shiny`, which is Posit’s package for Python.

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
- **Dummy Data**: The file `dummy_data_for_practice.csv` is included for you to test the app’s functionality with dummy data. Please free to use your own data!
- **VS Code Configuration**: If you use VS Code, you may want to install the `Shiny for Python` extension, which will help you run the app and display the content in an in-window browser.
