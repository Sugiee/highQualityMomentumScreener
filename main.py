import numpy as np
import pandas as pd
import requests
import math
import scipy
from scipy.stats import percentileofscore as score # calc percentile scores and pic top 50 percentile stocks
import xlsxwriter

# import list of stocks
stocks = pd.read_csv('sp_500_stocks.csv')

# parsing API calls
from secrets_ import IEX_CLOUD_API_TOKEN

# batch API calls to improve performance
def chunks(lst, n):     # used to split list of stocks in to sub-lists
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        
symbol_groups = list(chunks(stocks['Ticker'], 100))     # 100 elements per sub-list
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))   # element split with ',' in list to separate
    
def portfolio_input():
    global portfolio_size
    portfolio_size = input('Enter the size of your portfolio: ')
    
    try:
        float (portfolio_size)
    except:
        print('That is not a number! \n Please try again: ')
        portfolio_size = input('Enter the size of your portfolio: ')
    
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
# Calculating number of shares to buy - Strategy 1 (low quality) 
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
   
# my_columns = ['Ticker', 'Price', 'One-Year Price Return', 'Number of Shares to Buy']

# final_dataframe = pd.DataFrame(columns = my_columns)

# for symbol_string in symbol_strings[:1]:
#     batch_api_call_url = f'https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=price,stats&token={IEX_CLOUD_API_TOKEN}'
#     data = requests.get(batch_api_call_url).json()      # base url, starts every http request + endpoint + token to let api know im allowed to use
#     for symbol in symbol_string.split(','):
#         if symbol == 'DISCA' or symbol == 'HFC' or symbol == 'VIAC' or symbol == 'WLTW' or symbol == 'ABC' or symbol == 'ANTM': # stocks where took out fund so stocks list outdated, API is unable to get info for these stocks
#             continue 
#         my_row =\
#         [
#             symbol,
#             data[symbol]['price'],
#             data[symbol]['stats']['year1ChangePercent'],
#             'N/A'            
#         ]
#         final_dataframe.loc[len(final_dataframe)] = my_row # add row of current stock data to dataframe
    
# # Removing Low-Momentum Stocks
# final_dataframe.sort_values('One-Year Price Return', ascending = False, inplace = True)
# final_dataframe = final_dataframe[:50]
# final_dataframe.reset_index(inplace = True)

#Calculating number of shares to buy - Strategy 1 (low quality)
# portfolio_input()

# portfolio_size = float(portfolio_size) / len(final_dataframe.index)
# for i in range(0, len(final_dataframe)):
#     final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(portfolio_size/final_dataframe.loc[i, 'Price'])

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
# Calculating number of shares to buy - Strategy 2 (high quality) Time series momentum metrics
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
hqm_columns = [
                'Ticker',
                'Price',
                'Number of Shares to Buy',
                'One-Year Price Return',
                'One-Year Return Percentile',
                'Six-Month Price Return',
                'Six-Month Return Percentile',
                'Three-Month Price Return',
                'Three-Month Return Percentile',
                'One-Month Price Return',
                'One-Month Return Percentile',
                'HQM Score'
              ]

hqm_dataframe = pd.DataFrame(columns = hqm_columns)

for symbol_string in symbol_strings: 
    batch_api_call_url = f'https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=price,stats&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()      # base url, starts every http request + endpoint + token to let api know im allowed to use
    for symbol in symbol_string.split(','):
        if symbol == 'DISCA' or symbol == 'HFC' or symbol == 'VIAC' or symbol == 'WLTW' or symbol == 'ABC' or symbol == 'ANTM' or symbol == 'FBHS' or symbol == 'NLOK' or symbol == 'RE': # stocks where took out fund so stocks list outdated, API is unable to get info for these stocks
            continue 
        my_row = [
                    symbol,
                    data[symbol]['price'],
                    'N/A',
                    data[symbol]['stats']['year1ChangePercent'],
                    'N/A',
                    data[symbol]['stats']['month6ChangePercent'],
                    'N/A',
                    data[symbol]['stats']['month3ChangePercent'],
                    'N/A',
                    data[symbol]['stats']['month1ChangePercent'],
                    'N/A',
                    'N/A'    
                 ]
        hqm_dataframe.loc[len(hqm_dataframe)] = my_row  

hqm_dataframe = hqm_dataframe.dropna()

# Calculating Momentum Percentiles
time_periods = [
                'One-Year',
                'Six-Month',
                'Three-Month',
                'One-Month'
                ]

for row in hqm_dataframe.index:
    for time_period in time_periods:
        change_col = f'{time_period} Price Return'
        percentile_col = f'{time_period} Return Percentile'
        hqm_dataframe.loc[row, percentile_col] = score(hqm_dataframe[change_col], hqm_dataframe.loc[row, change_col])/100

# Calculating the High-Quality Momentum (HQM) Score
# is the mean of the 4 momentum percentile scores
from statistics import mean

for row in hqm_dataframe.index:
    momentum_percentiles = []
    for time_period in time_periods:
        momentum_percentiles.append(hqm_dataframe.loc[row, f'{time_period} Return Percentile'])
    hqm_dataframe.loc[row,'HQM Score'] = mean(momentum_percentiles) 

# Selecting the 50 Best Momentum Stocks
hqm_dataframe.sort_values('HQM Score', ascending = False, inplace = True)
hqm_dataframe = hqm_dataframe[:50]
hqm_dataframe.reset_index(drop = True, inplace = True)

# Calculate the number of shares to buy
portfolio_input()
portfolio_size = float(portfolio_size)/len(hqm_dataframe.index)

for i in hqm_dataframe.index:
    hqm_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(portfolio_size/hqm_dataframe.loc[i, 'Price'])
    
print(hqm_dataframe)

# Format Our Excel Output
writer = pd.ExcelWriter('momentum_strategy.xlsx', engine='xlsxwriter')
hqm_dataframe.to_excel(writer, sheet_name='Momentum Strategy', index = False)

background_colour = '#0a0a23'
font_colour = '#ffffff'

string_format = writer.book.add_format(
    {
        'font_color' : font_colour,
        'bg_color' : background_colour,
        'border' : 1
    }    
)
pound_format = writer.book.add_format(
    {
        'num_format' : '£0.00',
        'font_color': font_colour,
        'bg_color' : background_colour,
        'border' : 1
    }    
) 
integer_format = writer.book.add_format(
    {
        'num_format' : '0',
        'font_color': font_colour,
        'bg_color' : background_colour,
        'border' : 1
    }    
)
float_format = writer.book.add_format(
    {
        'num_format' : '0.00',
        'font_color': font_colour,
        'bg_color' : background_colour,
        'border' : 1
    }    
)
percent_format = writer.book.add_format(
        {
            'num_format':'0.00%',
            'font_color': font_colour,
            'bg_color': background_colour,
            'border': 1
        }
    )

column_formats = { 
                    'A': ['Ticker', string_format],
                    'B': ['Price', pound_format],
                    'C': ['Number of Shares to Buy', integer_format],
                    'D': ['One-Year Price Return', percent_format],
                    'E': ['One-Year Return Percentile', percent_format],
                    'F': ['Six-Month Price Return', percent_format],
                    'G': ['Six-Month Return Percentile', percent_format],
                    'H': ['Three-Month Price Return', percent_format],
                    'I': ['Three-Month Return Percentile', percent_format],
                    'J': ['One-Month Price Return', percent_format],
                    'K': ['One-Month Return Percentile', percent_format],
                    'L': ['HQM Score', float_format]
                    }

for column in column_formats.keys():
    writer.sheets['Momentum Strategy'].set_column(f'{column}:{column}', 20, column_formats[column][1])
    writer.sheets['Momentum Strategy'].write(f'{column}1', column_formats[column][0], string_format)
    
writer._save()
