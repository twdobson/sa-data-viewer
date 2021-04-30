import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app.models import db, MonthlyTimeSeries


def init_dash_app(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/',
        external_stylesheets=[
            '/static/dist/css/styles.css',
        ]
    )

    dash_app.layout = html.Div(
        id='dash-container',
        children=[
            html.H5("HELLO DASH"),
            html.Button(id='button-button'),
            html.H5(id='text-out', children='H'),
            html.H5(id='text-out2', children='NEW'),
            dcc.Dropdown(id='drop')
        ]
    )

    init_callbacks(app=dash_app)

    return dash_app.server


def init_callbacks(app):
    @app.callback(
       [Output('text-out2', "children"),Output('drop', "options")],

        Input('button-button', 'n_clicks')
    )
    def add_button(nclicks):
        print(nclicks)
        monthly_time_series = MonthlyTimeSeries(
            industry=str(nclicks) if nclicks else 'NOPE',
            year_month=202001,
            index=1111,
        )

        db.session.add(monthly_time_series)
        db.session.commit()

        q = MonthlyTimeSeries.query.all()
        # q = pd.read_sql(select([MonthlyTimeSeries]), db.session.bind)

        return (
            [r.id for r in q] if q else "ERROR",
            [{"label": r.id, "value":r.id} for r in q]
        )

