import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from plotly.tools import DIAG_CHOICES
from app.design.fonts import AppFont
from app.models import RetailMonthlyTimeSeries, RetailSeries, db
from app.views.components import sidebar
from dash import no_update
from dash.dependencies import Input, Output
from helper_functions.io import (create_label_value_pairs_from_series,
                                 read_sql_to_pandas)
from sqlalchemy import and_, select
import plotly.express as px
import pandas as pd

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


def get_indices_layout():
    layout = [
        sidebar,
        html.Div(
            id='div-dropdowns',
            children=[
                html.Div([
                    html.Label(
                        [
                            "Select an industry",
                            dcc.Dropdown(
                                id='dropdown-industry',
                                multi=True,
                                style={'width': 303, 'font-size': AppFont.font_size},
                                optionHeight=60
                            ),
                        ]
                    ),
                    html.Label(
                        [
                            "Select price definition",
                            dcc.Dropdown(
                                id='dropdown-prices',
                                multi=True,
                                style={'width': 303, 'font-size': AppFont.font_size}
                            ),
                        ]
                    ),
                    html.Label(
                        [
                            "Select Seasonality",
                            dcc.Dropdown(
                                id='dropdown-actual-or-adjusted',
                                multi=True,
                                style={'width': 303, 'font-size': AppFont.font_size}
                            ),
                        ]
                    ),
                ],
                    style={'display': 'inline-block'}
                ),
                html.Hr(),
                html.Div([
                    html.Label(
                        [
                            "Select Index Year",
                            dcc.Dropdown(id='dropdown-index-year-month')
                        ]
                    )
                ]
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Loading(
                                    id="loading-line-indice-graph",
                                    children=[
                                        html.Div(
                                            dcc.Graph(
                                                id='line-indice-graph',
                                                # style={'width': '66%'},
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
                        html.Div(
                            [
                                html.Div(
                                    dcc.Graph(
                                        id='pie-indice-graph',
                                    ),

                                ),
                            ],
                            style={
                                "border": "1px rgba(206,207,208,0.15) solid", 'width': '39%', 'display': 'inline-block', 'vertical-align': 'top'
                            }
                        )
                    ],
                ),
            ],

            style={**CONTENT_STYLE, **{"background-color": "#f8f9fa"}}
        ),

    ]

    return layout


def init_callbacks(app):

    @app.callback(

        Output('line-indice-graph', 'figure'),

        [
            Input("dropdown-index-year-month", "value"),
            Input('dropdown-industry', 'value'),
            Input('dropdown-prices', 'value'),
            Input('dropdown-actual-or-adjusted', 'value'),
        ]
    )
    def plot_pie_graph(year_month, industry, prices, actual_or_adjusted):
        if industry is None or prices is None or actual_or_adjusted is None:
            return no_update

        else:
            sql_query = select([
                RetailMonthlyTimeSeries.spend,
                RetailMonthlyTimeSeries.year_month,
                RetailMonthlyTimeSeries.retail_series_id,
                RetailSeries.industry,
                RetailSeries.prices,
                RetailSeries.actual_or_adjusted
            ]).where(
                and_(
                    RetailMonthlyTimeSeries.retail_series_id == RetailSeries.id,
                    # RetailSeries.year_month.isin_(year_month),
                    RetailSeries.industry.in_(industry),
                    RetailSeries.actual_or_adjusted.in_(actual_or_adjusted),
                    RetailSeries.prices.in_(prices)
                )
            )

            df = pd.read_sql(sql_query, db.session.bind)
            if year_month:
                series_index_spend_map = df.loc[
                    df['year_month'] == year_month
                ].set_index('retail_series_id')['spend'].to_dict()

                df['index_spend'] = df['retail_series_id'].map(series_index_spend_map)

                df['base_100_spend'] = df['spend'] / df['index_spend'] * 100

            fig = px.line(
                df,
                x="year_month",
                y="spend" if year_month is None else 'base_100_spend',
                color="retail_series_id",
                title='Retail spend indicies'
                # hover_name="country",
                # log_x=True, size_max=55
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

        Output('pie-indice-graph', 'figure'),
        # Output('loading-line-indice-graph', 'children')

        [
            Input("dropdown-index-year-month", "value"),
            Input('dropdown-industry', 'value'),
            Input('dropdown-prices', 'value'),
            Input('dropdown-actual-or-adjusted', 'value'),
        ]
    )
    def plot_indice_graph(year_month, industry, prices, actual_or_adjusted):

        if industry is None or prices is None or actual_or_adjusted is None:
            return no_update

        else:
            sql_query = select([
                RetailMonthlyTimeSeries.spend,
                RetailMonthlyTimeSeries.year_month,
                RetailMonthlyTimeSeries.retail_series_id,
                RetailSeries.industry,
                RetailSeries.prices,
                RetailSeries.actual_or_adjusted
            ]).where(
                and_(
                    RetailMonthlyTimeSeries.retail_series_id == RetailSeries.id,
                    # RetailSeries.year_month.isin_(year_month),
                    # RetailSeries.industry.in_(industry),
                    RetailSeries.actual_or_adjusted.in_(actual_or_adjusted),
                    RetailSeries.prices.in_(prices)
                )
            )

            df = pd.read_sql(sql_query, db.session.bind)
            total = df[(
                df['industry'] == 'Total')
            ].groupby(
                'industry'
            )['spend'].sum().values[0]

            non_totals = df[
                df['industry'] != 'Total'
            ].groupby(
                ['industry'], as_index=False
            )['spend'].sum()

            non_totals['proportion'] = non_totals['spend'] / total

            included = non_totals[non_totals['industry'].isin(industry)]
            non_included = non_totals[~non_totals['industry'].isin(industry)]
            non_included['industry'] = 'Other Industries'

            combined_pie_chart_data = pd.concat([
                included,
                non_included.groupby('industry', as_index=False).sum()
            ])

            fig = px.pie(
                combined_pie_chart_data,
                values='spend',
                names='industry',
                title='Composition of total spend'
            )

            fig.update_layout(transition_duration=500)
            fig.update_layout(
                paper_bgcolor='rgba(255,255,255,100)',
                plot_bgcolor='rgba(255,255,255,100)',
                legend=dict(
                    # x=0,
                    # y=1,
                    orientation="h",
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
        [
            Output("dropdown-index-year-month", "options"),
            Output('dropdown-industry', 'options'),
            Output('dropdown-prices', 'options'),
            Output('dropdown-actual-or-adjusted', 'options'),
            # Output('dropdown-menu-industry', 'label'),
        ],
        Input("div-dropdowns", "children")
    )
    def set_dropdown_options(
        placeholder
    ):

        index_year_options = create_label_value_pairs_from_series(
            series={
                indice.year_month
                for indice
                in db.session.query(RetailMonthlyTimeSeries.year_month)
            }
        )

        industry_options = create_label_value_pairs_from_series(
            series={
                indice.industry
                for indice
                in db.session.query(RetailSeries.industry)
            }
        )

        prices_options = create_label_value_pairs_from_series(
            series={
                indice.prices
                for indice
                in db.session.query(RetailSeries.prices)
            }
        )

        acrual_or_adjusted_options = create_label_value_pairs_from_series(
            series={
                indice.actual_or_adjusted
                for indice
                in db.session.query(RetailSeries.actual_or_adjusted)
            }
        )

        return (
            index_year_options,
            industry_options,
            prices_options,
            acrual_or_adjusted_options,
            # [{option:option} for option in industry_options if option.get('value') != 'Total']
        )

        # @app.callback(
        #     Output('graph-with-slider', 'figure'),
        #     Input('year-month-range-slider', 'value'))
        # def update_figure(selected_year):

        #     read_sql_to_pandas(
        #         sql=select(
        #             [RetailMonthlyTimeSeries]
        #         ).where(
        #             RetailMonthlyTimeSeries.year_month <=
        #         )
        #     )

        #     fig = px.scatter(filtered_df, x="gdpPercap", y="lifeExp",
        #                     size="pop", color="continent", hover_name="country",
        #                     log_x=True, size_max=55)

        #     fig.update_layout(transition_duration=500)

        #     return fig

        @ app.callback(
            [Output('text-out2', "children"), Output('drop', "options")],
            Input('button-button', 'n_clicks')
        )
        def add_button(nclicks):

            # print(nclicks)
            # monthly_time_series = MonthlyTimeSeries(
            #     industry=str(nclicks) if nclicks else 'NOPE',
            #     year_month=202001,
            #     index=1111,
            # )

            # monthly_time_series = MonthlyTimeSeries.query.all()

            # df = pd.DataFrame({'industry': ['stuff_you'], "year_month":[202003], 'index': [202]})
            # df = pd.DataFrame({'industry': [1], "year_month":['nice'], 'index': [202]})
            # db.drop_all()
            # db.create_all()
            # db.session.commit()
            # db.session.bulk_insert_mappings(MonthlyTimeSeries, df.to_dict(orient='records'))

            # db.session.add(monthly_time_series)
            # db.session.commit()

            # q[0].industry
            q = RetailMonthlyTimeSeries.query.all()
            # q = pd.read_sql(select([MonthlyTimeSeries]), db.session.bind)

            return (
                [r.id for r in q] if q else "ERROR",
                [{"label": r.id, "value": r.id} for r in q]
            )
