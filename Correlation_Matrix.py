# %% [markdown]
# # Stock Data Correlation Analysis
# 
# This notebook performs an analysis of stock market data, focusing on the calculation of normalized returns and correlation matrices between different companies over various time windows. We will use this analysis to generate heatmaps, visualizing the correlation between the companies.
# 
# ## 1. Import Libraries
# 
# We begin by importing the necessary libraries for data extraction, processing, and visualization.
# - `os`: For navigating through directories and files.
# - `pandas`: To handle and manipulate structured data.
# - `numpy`: To perform numerical operations.
# - `scipy.stats`: For statistical calculations.
# - `matplotlib.pyplot`: For visualizing data using plots and heatmaps.

# %%
import os
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# %% [markdown]
# ## 2. Extract Stock Data
# 
# The `extract_data` function is used to extract stock data from a folder structure where each folder represents a category, and each file inside a folder contains stock data for a company. 
# 
# The extracted data consists of:
# - `Date`: The date of the stock market entry.
# - `Open`: The opening stock price for that day.
# - `Close`: The closing stock price for that day.

# %%
def extract_data(main_folder):
    """
    This function extracts stock data from CSV files in the given folder structure.
    
    Args:
        main_folder (str): Path to the folder containing categories of companies.
        
    Returns:
        stock_data (dict): A dictionary where the keys are company names and values are dataframes containing 'Date', 'Open', and 'Close' stock prices.
    """
    stock_data = {}
    dirs = [d for d in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, d))]
    for category in dirs:
        category_path = os.path.join(main_folder, category)
        for company_file in os.listdir(category_path):
            if company_file.endswith('.csv'):
                company_name = company_file.split('.')[0]
                company_path = os.path.join(category_path, company_file)
                df = pd.read_csv(company_path)
                df = df[['Date', 'Open', 'Close']]
                stock_data[company_name] = df
    return stock_data

# %% [markdown]
# ## 3. Calculate Normalized Returns
# 
# The `calculate_normalized_returns_zero_mean` function normalizes the stock returns using a sliding window approach. We subtract the mean of the window and divide by the standard deviation to obtain a zero-mean, unit-variance normalized return.

# %%
def calculate_normalized_returns_zero_mean(returns, window_size=13):
    """
    Calculate the normalized returns r*(t) over a specified window size.
    
    Args:
        returns (np.array): Array of daily returns.
        window_size (int): The size of the sliding window.
        
    Returns:
        np.array: The normalized returns for the given window size.
    """
    normalized_returns = []
    for window in np.array_split(returns, window_size):
        for ret in window:
            r_star_window = (ret - np.mean(window)) / np.std(window)
            np.seterr(divide='ignore', invalid='ignore')  # Ignore divide by zero warnings
            normalized_returns.append(r_star_window)
    return stats.zscore(np.asarray(normalized_returns))  # Return as z-scores for better normalization

# %% [markdown]
# ## 4. Calculate Correlation Coefficient Matrices
# 
# The `calculate_correlation_matrices_per_window` function computes the correlation coefficient matrix for multiple companies over a series of time windows. Each window contains a fixed number of days (44 days in this case), and the function outputs a list of correlation matrices for each time window.

# %%
def calculate_correlation_matrices_per_window(stock_data, window_size=44):
    """
    Calculate the correlation coefficient matrices for multiple companies over different time windows.
    
    Args:
        stock_data (dict): A dictionary of stock dataframes with normalized returns.
        window_size (int): The size of each time window for correlation calculations.
        
    Returns:
        list: A list of correlation matrices (dataframes) for each window.
    """
    company_names = list(stock_data.keys())
    num_companies = len(company_names)
    correlation_matrices = []

    first_company = company_names[0]
    windows_count = len(stock_data[first_company]['Normalized_Return']) // window_size
    
    for win_num in range(windows_count):
        correlation_matrix = np.zeros((num_companies, num_companies))
        for i in range(num_companies):
            for j in range(i, num_companies):
                df_i = stock_data[company_names[i]]
                df_j = stock_data[company_names[j]]

                window_i = np.array_split(df_i['Normalized_Return'].values, len(df_i) // window_size)
                window_j = np.array_split(df_j['Normalized_Return'].values, len(df_j) // window_size)

                if len(window_i[win_num]) > 1 and len(window_j[win_num]) > 1:
                    Cij_num_win = np.corrcoef(window_i[win_num], window_j[win_num])[0][1]
                else:
                    Cij_num_win = np.nan

                correlation_matrix[i, j] = Cij_num_win
                correlation_matrix[j, i] = Cij_num_win
        correlation_matrices.append(pd.DataFrame(correlation_matrix, index=company_names, columns=company_names))

    return correlation_matrices


# %% [markdown]
# ## 5. Plot Heatmaps of Correlation Matrices
# 
# The `heat_map` function generates a heatmap for each time window to visualize the correlation matrices. The heatmaps use a blue color scale to show correlations between companies, where darker colors represent higher correlations.
# 

# %%
def heat_map(correlation_matrices, stock_data):
    """
    Plot heatmaps of the correlation matrices for each time window.
    
    Args:
        correlation_matrices (list): A list of correlation coefficient matrices.
        stock_data (dict): Stock data for labeling purposes.
    """
    for num, window in enumerate(correlation_matrices):
        plt.imshow(window.to_numpy(), cmap='Blues', vmin=-1, vmax=1)
        plt.colorbar()
        plt.title(f"Window {num}")
        plt.xlabel("Company")
        plt.ylabel("Company")
        plt.xticks([], [])
        plt.yticks([], [])
        plt.savefig(f'Window_{num}.png', dpi=300)
        plt.show()

# %% [markdown]
# ## 6. Running the Analysis
# 
# We extract the stock data, calculate returns and normalized returns, and then compute the correlation matrices for each time window. Finally, we plot the heatmaps to visualize the correlations.
# 

# %%
# Define the path to the folder containing the stock data
main_folder = r"D:\My physics project\Econophysics\Data\Data_Ex2\pure"

# Extract stock data from the folder
stock_data = extract_data(main_folder)

# Loop through each company to calculate returns and normalized returns
for company, df in stock_data.items():
    df['Return'] = (df['Close'] - df['Open']) / df['Open']
    df['Normalized_Return'] = calculate_normalized_returns_zero_mean(df['Return'].values)

# Calculate correlation matrices
correlation_results = calculate_correlation_matrices_per_window(stock_data)

# Plot heatmaps of the correlation matrices
heat_map(correlation_results, stock_data)


