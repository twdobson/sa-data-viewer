import pandas as pd

pd.options.display.max_rows = 500
pd.options.display.max_columns = 5100
pd.options.display.width = 2000
pd.options.display.max_colwidth = 1000

df = pd.read_html('./data_assets/stats_sa/Retail trade sales from 2002.xls')[0]

retail_trade_series_column_map = {
    'H01': 'publication_id',
    'H02': 'publication',
    'H03': 'label',
    'H04': 'split',
    'H05': 'industry',
    'H15': 'prices',
    'H17': 'actual_or_adjusted'
}



index_columns = df.columns[df.columns.str.contains('H')]
monthly_columns = df.columns.drop(index_columns)

melted_df = pd.melt(
    frame=df,
    id_vars=index_columns,
    value_vars=monthly_columns,
    var_name='month',
    value_name='index'
)

import numpy as np

melted_df.loc[melted_df['index'] == '.', 'index'] = None
melted_df.dropna(subset=['index'], inplace=True)
melted_df['index'] = melted_df['index'].astype(int) * 1_000_000
melted_df['year_month'] = melted_df['month'].str.slice(4, 8) + melted_df['month'].str.slice(2, 4)


melted_df.rename(columns=retail_trade_series_column_map, inplace=True)
melted_df['industry'] = melted_df['industry'].fillna('Total')



monthly_time_series = melted_df.rename()[['series_id', 'year_month', 'index']]

series = melted_df[['label', ]]



df.head()
