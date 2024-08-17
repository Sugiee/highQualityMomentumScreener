# High-Quality Momentum (HQM) Stock Selection Strategy

## Overview:

  This project implements a High-Quality Momentum (HQM) stock selection strategy using Python. The strategy involves selecting the top 50 momentum stocks from the S&P 500 index based on their one-year, six-month, 
  three-month, and one-month price returns. The strategy then calculates the number of shares to buy for each stock based on the user's portfolio size.

### Project Structure:

    sp_500_stocks.csv: A CSV file containing the ticker symbols of S&P 500 stocks.

    momentum_strategy.xlsx: The output Excel file that lists the top 50 momentum stocks and relevant metrics.

    secrets_.py: A Python file (not included) containing your IEX_CLOUD_API_TOKEN to access the IEX Cloud API.

### How It Works:

  1. Importing Required Libraries
  The script imports necessary libraries such as pandas, numpy, requests, and others needed for data manipulation, API calls, and statistical calculations.
  
  2. Fetching Stock Data
  Using the IEX Cloud API, the script fetches the current price and price return data (one-year, six-month, three-month, and one-month) for all S&P 500 stocks.
  
  3. Calculating Momentum Percentiles
  The momentum percentile is calculated for each stock based on its returns over different time periods. These percentiles are used to compute an overall HQM score.
  
  4. Selecting the Top 50 Stocks
  The script sorts the stocks based on their HQM scores and selects the top 50 stocks with the highest momentum.
  
  5. Calculating Number of Shares to Buy
  The number of shares to buy for each stock is calculated based on the user's total portfolio size and the stock's price.
  
  6. Exporting to Excel
  The final list of stocks, along with their metrics, is exported to an Excel file (momentum_strategy.xlsx). The Excel file is formatted for better readability.

### Example output:
![image](https://github.com/user-attachments/assets/5b15cded-b4b5-49a2-9568-ae6acdd94e23)

