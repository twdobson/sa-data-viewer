import pandas as pd
from pytrends.request import TrendReq
import numpy as np
from datetime import datetime

PD_MAX_ROWS = 500
PD_MAX_COLUMNS = 5100
PD_CONSOLE_WIDTH = 2000
PD_MAX_COLWIDTH = 1000

pd.options.display.max_rows = PD_MAX_ROWS
pd.options.display.max_columns = PD_MAX_COLUMNS
pd.options.display.width = PD_CONSOLE_WIDTH
pd.options.display.max_colwidth = PD_MAX_COLWIDTH

SEARCH_VALUE = 'pornhub'


pytrends = TrendReq(hl='en-US', geo='ZA')


START_DATE = pd.to_datetime('2016-01-01')
END_DATE = pd.to_datetime('2021-05-16')

full_date_range = pd.DataFrame({
    'date_index': pd.date_range(START_DATE, END_DATE)
})


# Note, hourly data is in UTC - this is the same as weekly data
# Need to adjust hours after apply adjustments based on weekly data
results_hourly_by_week = pytrends.get_historical_interest(
    ['pornhub'],
    year_start=START_DATE.year,
    month_start=START_DATE.month,
    day_start=START_DATE.day,
    hour_start=0,
    year_end=END_DATE.year,
    month_end=END_DATE.month,
    day_end=END_DATE.day,
    hour_end=23,
    cat=0,
    geo='ZA',
    gprop='',
    sleep=0.025
)


hourly_trends = results_hourly_by_week.reset_index().rename(
    columns={'date': 'timestamp'}
)

hourly_trends['date'] = pd.to_datetime(hourly_trends['timestamp'].dt.date)


# Set weeks to start on a Sunday (weekday = 6)
# We only need to offset non-sunday days, as Sunday's date is the start of the week
hourly_trends['week_start_date'] = np.where(
    hourly_trends['date'].dt.weekday == 6,
    hourly_trends['date'],
    hourly_trends['date'] - pd.offsets.Week(weekday=6)
)

hourly_trends = pd.merge(
    full_date_range,
    hourly_trends,
    left_on=['date_index'],
    right_on=['date'],
    how='left'
)


# days without 24 hours of data need to be repulled
issue_days = hourly_trends.groupby('date_index')['timestamp'].count()
issue_days = issue_days[(issue_days < 24)].index

print('repulling failed weekly data')
repulled_issue_days = [
    pytrends.get_historical_interest(
        ['pornhub'],
        year_start=day.year,
        month_start=day.month,
        day_start=day.day,
        hour_start=0,
        year_end=day.year,
        month_end=day.month,
        day_end=day.day,
        hour_end=23,
        cat=0,
        geo='ZA',
        gprop='',
        sleep=0.025
    )
    for day
    in issue_days
]
print('done')

df_repulled_issue_days = pd.concat(
    repulled_issue_days,
    axis=0
).reset_index().rename(
    columns={'date': 'timestamp'}
)

df_repulled_issue_days['date'] = pd.to_datetime(
    df_repulled_issue_days['timestamp'].dt.date
)
df_repulled_issue_days['week_start_date'] = np.where(
    df_repulled_issue_days['date'].dt.weekday == 6,  # offset on Non Sundays
    df_repulled_issue_days['date'],
    df_repulled_issue_days['date'] - pd.offsets.Week(weekday=6)
)


df_repulled_issue_days = pd.merge(
    full_date_range,
    df_repulled_issue_days,
    left_on=['date_index'],
    right_on=['date'],
    how='left'
).dropna()


# remove issue data from trends data and add the repulled data
hourly_trends['hours_in_day'] = hourly_trends.groupby(
    'date_index'
)['timestamp'].transform('count')

hourly_trends = hourly_trends[hourly_trends['hours_in_day'] >= 24]
hourly_trends_repulled = pd.concat(
    [hourly_trends, df_repulled_issue_days]
).sort_values('date_index')


# rejoin full date range
# now we set weeks which are 100% 0 to null and then we impute nulls
hourly_trends_repulled = pd.merge(
    full_date_range,
    hourly_trends_repulled.drop(columns=['date_index']),
    left_on=['date_index'],
    right_on=['date'],
    how='left'
)


hourly_trends_repulled.groupby('date_weekly').size()

hourly_trends_repulled['mean_week_trend'] = hourly_trends_repulled.groupby(
    'date_index'
)[SEARCH_VALUE].transform('mean')

hourly_trends_repulled.loc[
    hourly_trends_repulled['mean_week_trend'] == 0,
    SEARCH_VALUE
] = None

hourly_trends_repulled['hour'] = hourly_trends_repulled['timestamp'].dt.hour
hourly_trends_repulled['day_of_week'] = hourly_trends_repulled['timestamp'].dt.day_of_week

hourly_trends_repulled['mean_hour_weekday_value'] = hourly_trends_repulled.groupby(
    ['day_of_week', 'hour']
)[SEARCH_VALUE].transform('mean')


hourly_trends_repulled.loc[
    hourly_trends_repulled[SEARCH_VALUE].isna(),
    SEARCH_VALUE
] = hourly_trends_repulled.loc[
    hourly_trends_repulled[SEARCH_VALUE].isna(),
    'mean_hour_weekday_value'
]


kw_list = ["pornhub"]
pytrends.build_payload(kw_list, cat=0, timeframe='today 5-y', geo='ZA', gprop='')
weekly_data_global_maximum = pytrends.interest_over_time()
weekly_data_global_maximum = weekly_data_global_maximum.reset_index()

#####################################


hourly_trends_repulled['join_date'] = hourly_trends_repulled['week_start_date'].astype(str)
hourly_trends_repulled['nth_in_group'] = hourly_trends_repulled.groupby('timestamp').cumcount() + 1
hourly_trends_repulled['size_of_group'] = hourly_trends_repulled.groupby('timestamp')['pornhub'].transform('size')

hourly_trends_repulled = hourly_trends_repulled.loc[
    (hourly_trends_repulled['size_of_group'] == 1)
    | ((hourly_trends_repulled['size_of_group'] == 2) & (hourly_trends_repulled['nth_in_group'] == 1))
]

weekly_data_global_maximum['join_date'] = weekly_data_global_maximum['date'].astype(str)

hourly_trends_repulled['total_views'] = hourly_trends_repulled.groupby('date_weekly')['pornhub'].transform('sum')

results = hourly_trends_repulled.merge(
    weekly_data_global_maximum,
    on='join_date',
    how='left',
    suffixes=('', '_weekly')
)

results.groupby('date_weekly').size()
hourly_trends_repulled.groupby('date_index')[SEARCH_VALUE].size()


results['total_views'] = results.groupby('date_weekly')['pornhub'].transform('sum')
results['scaled_series_2'] = results['pornhub'] / results["total_views"] / 100
results['scaled_series_3'] = results['scaled_series_2'] * results['pornhub_weekly']

# s = results.groupby('c')['scaled_series'].mean()
import matplotlib.pyplot as plt
(results[results['date'] > pd.to_datetime('2019-12-29 ')].groupby('date_weekly')[
    'scaled_series_3'].sum() * 100).reset_index()['scaled_series_3'].plot(ylim=(0, 100))
weekly_data_global_maximum[
    (weekly_data_global_maximum['date'] >= pd.to_datetime('2019-12-29'))
    & (weekly_data_global_maximum['date'] <= pd.to_datetime('2020-12-27'))
].reset_index()['pornhub'].plot(ylim=(0, 100))

plt.savefig('./avg_week.jpeg')
plt.close()


results['scaled_series_3'].iloc[0:300].plot()
#           date  pornhub isPartial   join_date
# 193 2020-01-19       78     False  2020-01-19
# 194 2020-01-26       72     False  2020-01-26
# 195 2020-02-02       77     False  2020-02-02
# 196 2020-02-09       76     False  2020-02-09
# 197 2020-02-16       75     False  2020-02-16

# 2.0      78.0
# 3.0      72.0
# 4.0      76.0
# 5.0      75.0
# 6.0      75.0
# 7.0      79.0

results.groupby('date_weekly').size()
results.groupby('date_weekly')['pornhub_weekly'].mean()

results['day_of_week'] = results['timestamp'].dt.day_name()
# results['day_of_week'] = results['timestamp'].dt.
results['hour'] = results['timestamp'].dt.hour
results.groupby(['hour', 'day_of_week'])['pornhub'].mean().reset_index()

results.groupby(['hour'])['pornhub'].mean().plot()


def df_to_plotly(df):
    return {'z': df['pornhub'].tolist(),
            'x': df['day_of_week'].tolist(),
            'y': df['hour'].tolist()}


import plotly.graph_objects as go

fig = go.Figure(data=go.Heatmap(df_to_plotly(results.groupby(['hour', 'day_of_week'])['pornhub'].mean().reset_index())))
fig.show()
fig.write_image("./fig1.jpeg")


results.iloc[1 * 24 * 7 - 2:]
results.iloc[2 * 24 * 7 - 2:]

results[results['c'] == 42]

results.shape
results['timestamp'].value_counts()[results['timestamp'].value_counts() == 2].sort_index()

results[results['timestamp'] == pd.to_datetime('2020-11-18 00:00:00')]

results.iloc[6960 - 10:6960 + 10]

weekly_data_global_maximum[weekly_data_global_maximum['date'] == pd.to_datetime('2020-01-19')]

hourly_trends.reset_index()['timestamp'].value_counts()
