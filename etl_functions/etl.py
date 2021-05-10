import geopandas as gpd
import pandas as pd
from app.models import Province, RetailMonthlyTimeSeries, RetailSeries, db
from manage import app

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


monthly_time_series, retail_series = prepare_monthly_time_series()

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

province = prepare_province()

province.to_postgis(
    name='Province',
    con=db.session.bind,
    if_exists='replace'
)
