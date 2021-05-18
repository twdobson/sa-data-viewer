from re import search
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from plotly.tools import DIAG_CHOICES
from app.design.fonts import AppFont
from app.models import RetailMonthlyTimeSeries, RetailSeries, db, GoogleTrends
from app.views.components import sidebar
from dash import no_update
from dash.dependencies import Input, Output
from helper_functions.io import (create_label_value_pairs_from_series,
                                 read_sql_to_pandas)
from sqlalchemy import and_, select
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

dropdown_menu_industry = dbc.DropdownMenu(
    [
        # dbc.DropdownMenuItem("Header", header=True),
        dbc.DropdownMenuItem("Total"),
        dbc.DropdownMenuItem(divider=True),
        # dbc.DropdownMenuItem("Active and disabled", header=True),
        # *[],
        dbc.DropdownMenuItem("Active item", active=True),
        dbc.DropdownMenuItem("Disabled item", disabled=True),
        dbc.DropdownMenuItem(divider=True),
    ],
    label="Select an industy",
    style={'width': 303, 'font-size': AppFont.font_size}
)


def get_layout():
    layout = [
        sidebar,
        html.Div(
            id='div-google-trends-dropdowns',
            children=[
                html.Div([
                    html.Label(
                        [
                            "Select a search term",
                            dcc.Dropdown(
                                id='dropdown-search-term',
                                multi=True,
                                style={'width': 303, 'font-size': AppFont.font_size},
                            ),
                        ]
                    ),
                ],
                    style={'display': 'inline-block'}
                ),
                html.Hr(),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Loading(
                                    id="loading-line-graph-google-trends",
                                    children=[
                                        html.Div(
                                            dcc.Graph(
                                                id='line-graph-google-trends',
                                            ),

                                        ),
                                    ],
                                    type="default"
                                ),
                            ],
                            className='divBorder',
                            style={
                                "border": "1px rgba(206,207,208,0.15) solid",
                                'width': '59%',
                                'display': 'inline-block',
                                "margin-right": "10px",
                                'vertical-align': 'top'
                            }
                        ),
                    ],
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Loading(
                                    id="loading-heatmap-graph-google-trends",
                                    children=[
                                        html.Div(
                                            dcc.Graph(
                                                id='heatmap-graph-google-trends',
                                            ),

                                        ),
                                    ],
                                    type="default"
                                ),
                            ],
                            className='divBorder',
                            style={
                                "border": "1px rgba(206,207,208,0.15) solid",
                                'width': '59%',
                                'display': 'inline-block',
                                "margin-right": "10px",
                                'vertical-align': 'top'
                            }
                        ),
                    ],
                ),
            ],

            style={**CONTENT_STYLE, **{"background-color": "#f8f9fa"}}
        ),

    ]

    return layout


def init_callbacks(app):

    @app.callback(

        Output('line-graph-google-trends', 'figure'),
        Input('dropdown-search-term', 'value'),
    )
    def plot_google_trend_line_graph(search_term):
        if search_term is None:
            return no_update

        else:
            sql_query = select([
                GoogleTrends.id,
                GoogleTrends.search_term,
                GoogleTrends.trend_index,
                GoogleTrends.week_start_date
            ]).where(
                GoogleTrends.search_term == search_term[0]
            )

            df = pd.read_sql(sql_query, con=db.session.bind)

            df.dropna(subset=['trend_index'], inplace=True)

            fig = px.line(
                df.groupby('week_start_date', as_index=False)['trend_index'].sum(),
                x="week_start_date",
                y='trend_index',
                # color="search_term",
                title='Google trend index'
            )

            fig.update_xaxes(type='category')
            fig.update_layout(transition_duration=500)
            fig.update_layout(
                paper_bgcolor='rgba(255,255,255,100)',
                plot_bgcolor='rgba(255,255,255,100)',
                legend=dict(
                    # x=0,
                    # y=1,
                    itemwidth=100,
                    traceorder="reversed",
                    title_font_family="Times New Roman",
                    font=dict(
                        family="Courier",
                        size=12,
                        color="black"
                    ),
                    bgcolor='rgba(0,0,0,0)',
                    # bordercolor="Black",
                    # borderwidth=2
                )
            )

            return fig

    @app.callback(
        Output("dropdown-search-term", "options"),
        Input("div-google-trends-dropdowns", "children")
    )
    def set_dropdown_options(
        placeholder
    ):

        search_term_options = create_label_value_pairs_from_series(
            series={
                indice.search_term
                for indice
                in db.session.query(GoogleTrends.search_term)
            }
        )

        return search_term_options

    @app.callback(

        Output('heatmap-graph-google-trends', 'figure'),
        Input('dropdown-search-term', 'value'),
    )
    def plot_heatmap_google_trends(search_term):

        if search_term is None:
            return no_update

        else:
            sql_query = select([
                GoogleTrends.id,
                GoogleTrends.search_term,
                GoogleTrends.trend_index,
                GoogleTrends.week_start_date,
                GoogleTrends.timestamp
            ]).where(
                GoogleTrends.search_term == search_term[0]
            )

            df = pd.read_sql(sql_query, con=db.session.bind)
            df['timestamp_local'] = df['timestamp'].dt.tz_convert('Africa/Johannesburg')
            df['time'] = df['timestamp_local'].dt.time.astype(str).str.slice(0, 5)
            df['day_of_week'] = df['timestamp_local'].dt.day_name()

            def df_to_heatmap(df, colour_column, x_axis_column, y_axis_column):
                return {
                    'z': df[colour_column].tolist(),
                    'x': df[x_axis_column].tolist(),
                    'y': df[y_axis_column].tolist()
                }

            week_day_order = [
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday'
            ]

            heatmap_data = df_to_heatmap(
                df=df.groupby(
                    ['time', 'day_of_week']
                )["trend_index"].mean().reset_index(),
                x_axis_column='day_of_week',
                y_axis_column='time',
                colour_column="trend_index"
            )

            # c = {
            #     'x': week_day_order,
            #     'y': [time[0:5] for time in pd.date_range("00:00", "23:00", freq="60min").time.astype(str).tolist()]
            # }

            fig = go.Figure(
                data=go.Heatmap(heatmap_data),
                layout=go.Layout(
                    xaxis={'title': 'Day of week', 'categoryarray': week_day_order},
                    yaxis={'title': 'Hour of day', 'categoryarray': [time[0:5] for time in pd.date_range("00:00", "23:00", freq="60min").time.astype(str).tolist()]},
                )
            )

            return fig

            # order = ['15-20', '20-25', '25-30', '30-35', '35-40']
            #     return {
            #         'data': [
            #             go.Heatmap(
            #                 z=fights['win_rate'],
            #                 y=fights['age_range'],
            #                 x=fights['opp_age_range'],
            #                 showscale=True)
            #         ],
            #         'layout': go.Layout(
            #             title='Wins rate by boxer age range',
            #             xaxis={'title':'Opposition age range','categoryarray': order},
            #             yaxis={'title': 'Boxer age range'},
            #             hovermode='closest',
            #             paper_bgcolor='black',
            #         )

            # import plotly.graph_objects as go
