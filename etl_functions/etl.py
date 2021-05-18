import geopandas as gpd
import pandas as pd
from app.models import Province, RetailMonthlyTimeSeries, RetailSeries, db, GoogleTrends
from manage import app
from datetime import datetime
import numpy as np

pd.options.display.max_rows = 500
pd.options.display.max_columns = 5100
pd.options.display.width = 2000
pd.options.display.max_colwidth = 1000

app.app_context().push()

db.drop_all()
db.create_all()
db.session.commit()

retail_trade_series_column_map = {
    'H01': 'publication_id',
    'H02': 'publication',
    'H03': 'label',
    'H04': 'split',
    'H05': 'industry',
    'H15': 'prices',
    'H16': 'actual_or_adjusted'
}

industry_renaming = {
    'Retailers in household furniture,appliances and equipment': 'Household goods',
    'General dealers': 'General dealers',
    'All other retailers': 'Other retailers',
    'Retailers in textiles,clothing,footwear and leather goods': 'Textiles and clothing',
    'Retailers in pharmaceutical and medical goods,cosmetics and toiletries': 'Pharmacies and health and beauty',
    'Retailers of food, beverages and tobacco in specialised stores': 'Specialised food, beverage and tobacco ',
    'Retailers in hardware,paint and glass': 'Hardware',
    "Total": 'Total'


}


def prepare_monthly_time_series() -> pd.DataFrame:
    raw_retail_trade_sales = pd.read_html('./data_assets/stats_sa/Retail trade sales from 2002.xls')[0]

    index_columns = raw_retail_trade_sales.columns[raw_retail_trade_sales.columns.str.contains('H')]
    monthly_columns = raw_retail_trade_sales.columns.drop(index_columns)

    melted_retail_trade_sales = pd.melt(
        frame=raw_retail_trade_sales,
        id_vars=index_columns,
        value_vars=monthly_columns,
        var_name='month',
        value_name='spend'
    )

    melted_retail_trade_sales.loc[melted_retail_trade_sales['spend'] == '.', 'spend'] = None
    melted_retail_trade_sales.dropna(subset=['spend'], inplace=True)
    melted_retail_trade_sales['spend'] = melted_retail_trade_sales['spend'].astype(int) * 1_000_000
    melted_retail_trade_sales['year_month'] = (
        melted_retail_trade_sales['month'].str.slice(4, 8) +
        melted_retail_trade_sales['month'].str.slice(2, 4)
    )

    melted_retail_trade_sales.rename(columns=retail_trade_series_column_map, inplace=True)
    melted_retail_trade_sales['industry'] = melted_retail_trade_sales['industry'].fillna('Total')
    melted_retail_trade_sales['industry'] = melted_retail_trade_sales['industry'].map(industry_renaming)

    melted_retail_trade_sales['retail_series_id'] = melted_retail_trade_sales.groupby(
        'label'
    ).ngroup()

    monthly_time_series = melted_retail_trade_sales[[
        'retail_series_id',
        'year_month',
        'spend'
    ]]

    retail_series = melted_retail_trade_sales[[
        'retail_series_id',
        'label',
        'split',
        'industry',
        'prices',
        'actual_or_adjusted'
    ]].rename(
        columns={'retail_series_id': 'id'}
    ).drop_duplicates()

    return monthly_time_series, retail_series


def prepare_province():

    province = gpd.read_file('./data_assets/PR_SA_2011')

    province_column_renaming = {
        'PR_CODE': 'id',
        'PR_NAME': 'label',
        'ALBERS_ARE': 'area',
    }

    province['PR_CODE'] = province['PR_CODE'].astype(int)
    province = province.rename(
        columns=province_column_renaming
    )[['id', 'label', 'area', 'geometry']]

    return province


def prepare_google_trends_data():

    SEARCH_VALUE = 'pornhub'
    START_DATE = pd.to_datetime('2016-01-01')
    END_DATE = pd.to_datetime('2021-05-16')

    full_timestamp_range = pd.DataFrame({
        'timestamp_index': pd.date_range(START_DATE, END_DATE, freq='H')
    })

    output_path = f'./data_assets/google_trends/hourly/{SEARCH_VALUE}/hourly.pkl'
    output_path_weekly = f'./data_assets/google_trends/weekly/{SEARCH_VALUE}/weekly.pkl'

    results_hourly_by_week = pd.read_pickle(output_path)
    weekly_data_global_maximum = pd.read_pickle(output_path_weekly)

    hourly_trends = results_hourly_by_week.reset_index().rename(
        columns={'date': 'timestamp'}
    )

    hourly_trends['date'] = pd.to_datetime(hourly_trends['timestamp'].dt.date)

    hourly_trends = pd.merge(
        full_timestamp_range,
        hourly_trends,
        left_on='timestamp_index',
        right_on='timestamp',
        how='left'
    )

    # hourly_trends['timestamp_index_date'] = hourly_trends

    hourly_trends['date_index'] = hourly_trends['timestamp_index'].dt.date
    hourly_trends['date_index'] = pd.to_datetime(hourly_trends['date_index'])

    hourly_trends['week_start_date'] = np.where(
        hourly_trends['date_index'].dt.weekday == 6,
        hourly_trends['date_index'],
        hourly_trends['date_index'] - pd.offsets.Week(weekday=6)
    )

    hourly_trends['week_start_date'].drop_duplicates()

    # remove issue data from trends data and add the repulled data
    hourly_trends['hours_in_day'] = hourly_trends.groupby(
        'date_index'
    )['timestamp'].transform('count')

    hourly_trends['mean_week_trend'] = hourly_trends.groupby(
        'date_index'
    )[SEARCH_VALUE].transform('mean')

    hourly_trends.loc[
        hourly_trends['mean_week_trend'] == 0,
        SEARCH_VALUE
    ] = None

    hourly_trends['hour'] = hourly_trends['timestamp_index'].dt.hour
    hourly_trends['day_of_week'] = hourly_trends['timestamp_index'].dt.day_of_week

    hourly_trends['mean_hour_weekday_value'] = hourly_trends.groupby(
        ['day_of_week', 'hour']
    )[SEARCH_VALUE].transform('mean')

    hourly_trends['mean_hour_weekday_value'].drop_duplicates()
    hourly_trends[hourly_trends['mean_hour_weekday_value'].isna()]

    hourly_trends.loc[
        hourly_trends[SEARCH_VALUE].isna(),
        SEARCH_VALUE
    ] = hourly_trends.loc[
        hourly_trends[SEARCH_VALUE].isna(),
        'mean_hour_weekday_value'
    ]

    hourly_trends['join_date'] = hourly_trends['week_start_date'].astype(str)
    hourly_trends['nth_in_group'] = hourly_trends.groupby('timestamp').cumcount() + 1
    hourly_trends['size_of_group'] = hourly_trends.groupby('timestamp')['pornhub'].transform('size')

    hourly_trends = hourly_trends.loc[
        (hourly_trends['size_of_group'] == 1)
        | ((hourly_trends['size_of_group'] == 2) & (hourly_trends['nth_in_group'] == 1))
        | (hourly_trends['nth_in_group'].isna())
        | (hourly_trends['size_of_group'].isna())
    ]

    weekly_data_global_maximum['join_date'] = weekly_data_global_maximum['date'].astype(str)

    # hourly_trends_repulled['total_views'] = hourly_trends_repulled.groupby('date_weekly')['pornhub'].transform('sum')

    results = hourly_trends.merge(
        weekly_data_global_maximum,
        on='join_date',
        how='left',
        suffixes=('', '_weekly')
    )

    hourly_trends['week_start_date'].drop_duplicates()
    # results.groupby('date_weekly').size()
    # hourly_trends_repulled.groupby('date_index')[SEARCH_VALUE].size()

    results['total_views'] = results.groupby('date_weekly')['pornhub'].transform('sum')
    results['scaled_series_2'] = results['pornhub'] / results["total_views"] / 100
    results['scaled_series_3'] = results['scaled_series_2'] * results['pornhub_weekly']

    results.columns

    results['search_term'] = SEARCH_VALUE
    google_trends_hourly = results[[
        'timestamp_index',
        'search_term',
        'week_start_date',
        'scaled_series_3'
    ]].rename(columns={
        # 'id': 'id',
        'timestamp_index': 'timestamp',
        'search_term': 'search_term',
        'week_start_date': 'week_start_date',
        'scaled_series_3': 'trend_index'
    })

    #     id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    # timestamp = db.Column(db.DateTime(timezone=True))
    # search_term = db.Column(db.String(64))
    # week_start_date = db.Column(db.Date)
    # trend_index = db.Column(db.Numeric)

    return google_trends_hourly


monthly_time_series, retail_series = prepare_monthly_time_series()

google_trends_hourly = prepare_google_trends_data()

db.session.bulk_insert_mappings(
    RetailSeries,
    retail_series.to_dict(orient='records')
)
db.session.commit()

db.session.bulk_insert_mappings(
    RetailMonthlyTimeSeries,
    monthly_time_series.to_dict(orient='records')
)

db.session.commit()

db.session.bulk_insert_mappings(
    GoogleTrends,
    google_trends_hourly.to_dict(orient='records')
)
db.session.commit()

province = prepare_province()

province.to_postgis(
    name='Province',
    con=db.session.bind,
    if_exists='replace'
)
