    rvm_app/
    │
    ├── bond_pricing/
    │   ├── __init__.py
    │   ├── calculations.py
    │   ├── data_processing.py
    │   ├── utils.py
    │   └── extended_bond_data.csv
    ├── andy_rvm.py
    ├── rvm_app.py
    ├── requirements.txt
    └── README.md

Description of Each File and Directory
bond_pricing/:
A Python package that encapsulates all backend functionalities related to bond pricing and RVM calculations.

__init__.py:
An empty file that indicates to Python that this directory should be treated as a package. It can also be used to import specific functions or classes for easier access.

calculations.py:
Contains functions responsible for performing regression analyses and creating Risk-Value Matrix (RVM) grids based on the regression results.

Key Functions:
perform_regressions(df, warf_map_sorted): Performs numerical and WARF-based regressions.
create_rvm_grids(ratings_order, durations, coeffs_num, coeffs_warf, warf_map): Generates RVM grids using regression coefficients.
data_processing.py:
Manages data loading and filtering operations. It processes the raw bond data and applies user-defined filters to prepare the dataset for analysis.

Key Functions:
load_data(file_path): Loads bond data from an Excel file.
filter_data(df, excluded_columns, country_list, min_notches, min_return): Filters the DataFrame based on user-selected criteria.
utils.py:
Contains utility functions for data visualization, including the creation of scatter plots, bar charts, and heatmaps.

Key Functions:
create_scatter_plot(df): Generates a scatter plot of OAS vs. OAD.
create_bar_chart(df): Creates a bar chart of expected returns by bond.
create_rvm_heatmap(rvm_df, title): Produces a heatmap for the RVM grid.
extended_bond_data.csv:
A CSV file containing extended information for each bond, primarily used for mapping ISINs to additional data such as country, credit notch, rating, ESG scores, and NFA indicators.

andy_rvm.py:
Contains core functions for performing regressions and creating RVM grids. This module includes functions like perform_regression, create_rvm_grid, and warf_to_rating_num.

Key Functions:
perform_regression(df, model_type, warf_map_sorted=None): Conducts regression analysis based on the specified model type.
create_rvm_grid(ratings_order, durations, model_type, coeffs, warf_map=None): Builds the RVM grid using regression coefficients.
warf_to_rating_num(rating): Converts WARF ratings to numerical values for analysis.
rvm_app.py:
The main Streamlit application file that serves as the entry point. It orchestrates the user interface, handles user interactions, and leverages backend functions for data processing, analysis, and visualization.

Key Features:
File Upload: Allows users to upload their own Excel files containing bond data.
Filters: Provides sidebar options to filter data by excluded columns, countries, minimum notches, and minimum expected returns.
Data Display: Shows the filtered bond data in a data frame.
Visualizations: Displays scatter plots, bar charts, and RVM heatmaps based on the filtered data.
Model Performance: Shows R-squared values for the regression models.
Download Option: Enables users to download the filtered data as a CSV file.
requirements.txt:
Lists all the Python dependencies required to run the application. This file ensures that all necessary packages are installed in the environment where the app is deployed.

README.md:
The documentation file you're currently creating. It provides an overview of the project, explains the directory structure, and offers guidance on installation and usage.

Installation
To set up and run rvm_app locally, follow these steps:

Clone the Repository:

bash
Copy code
git clone https://github.com/yourusername/rvm_app.git
cd rvm_app
Create a Virtual Environment:

It's recommended to use a virtual environment to manage dependencies.

bash
Copy code
python -m venv venv
Activate the Virtual Environment:

Windows:

bash
Copy code
venv\Scripts\activate
macOS/Linux:

bash
Copy code
source venv/bin/activate
Install Dependencies:

bash
Copy code
pip install --upgrade pip
pip install -r requirements.txt
Usage
Run the Streamlit App:

bash
Copy code
streamlit run rvm_app.py
Access the Application:

Once the app is running, open your web browser and navigate to the URL provided in the terminal (usually http://localhost:8501).

Interact with the Dashboard:

Upload Bond Data: Use the sidebar to upload your Excel file containing bond data.
Apply Filters: Select columns to exclude, choose countries, and set minimum notches and expected returns.
View Results: Explore the filtered data, interactive scatter plots, bar charts, and RVM heatmaps.
Download Data: Download the filtered dataset as a CSV file using the download button.
Dependencies
The application relies on the following Python packages:

streamlit: Web application framework for creating interactive dashboards.
pandas: Data manipulation and analysis.
plotly: Interactive graphing library.
numpy: Numerical operations.
openpyxl: Reading and writing Excel files.
streamlit-aggrid: Advanced grid display within Streamlit.
scikit-learn: Machine learning library used for regression analyses.
All dependencies are listed in the requirements.txt file. Ensure you have the latest versions by running:

bash
Copy code
pip install --upgrade -r requirements.txt
Contributing
Contributions are welcome! If you'd like to improve the project, please follow these steps:

Fork the Repository:

Click the "Fork" button at the top right of the repository page.

Create a New Branch:

bash
Copy code
git checkout -b feature/YourFeatureName
Make Your Changes:

Implement your feature or fix the issue.

Commit Your Changes:

bash
Copy code
git commit -m "Add Your Feature"
Push to the Branch:

bash
Copy code
git push origin feature/YourFeatureName
Create a Pull Request:

Navigate to your forked repository and click "Compare & pull request."

License
This project is licensed under the MIT License.