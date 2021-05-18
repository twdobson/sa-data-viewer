import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from app.auth import login, register
from app.views import components, home_page, indices, map_frame, google_trends
from dash.dependencies import Input, Output
from helper_functions.dash import get_callback_trigger


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# link fontawesome to get the chevron icons


# from flask import url_for, re
# return redirect(url_for('auth.login'))


# def init_dash_app(server):
#     """Create a Plotly Dash dashboard."""
#     dash_app = dash.Dash(
#         server=server,
#         routes_pathname_prefix='/dash/',
#         external_stylesheets=[dbc.themes.BOOTSTRAP, FA]
FA = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"
#         # external_stylesheets=[external_stylesheets]
#     )

# server.app_context().push()

import base64
encoded_image = base64.b64encode(open('app/assets/logo.jpeg', 'rb').read())

links = dbc.Row(
    [
        dbc.Col(dbc.Input(type="search", placeholder="Search")),
        dbc.Col(
            dbc.NavItem(dbc.NavLink(
                "Login",
                id='link',
                href="/login",
                external_link=True)
            ),
            width="auto",
        ),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(
                        html.Img(
                            src='data:image/png;base64,{}'.format(
                                encoded_image.decode()
                            ), height="30px")
                    ),
                    dbc.Col(dbc.NavbarBrand("Navbar", className="ml-2")),

                ],
                align="left",
                no_gutters=True,
            ),
            href="/dashapp/",
        ),
        links,
        # dbc.NavbarToggler(id="navbar-toggler"),
        # dbc.Collapse(search_bar, id="navbar-collapse", navbar=True),
    ],
    color="dark",
    dark=True,
    # brand="My Analytics Dashboard",
    # brand_href="#",
    # color="#3C8DBC",
    # dark=True,
    fixed="top",
    # brand_style={'textAlign': 'left'},

)

layout = html.Div(
    id='dash-container',
    children=[
        dcc.Location(id="url"),
        navbar,
        html.Br(),
        html.Br(),
        html.Div(id='content-pane')
    ]
)


def init_callbacks(dash_app):

    components.init_callbacks(dash_app)
    indices.init_callbacks(app=dash_app)
    google_trends.init_callbacks(app=dash_app)
    # login.init_callbacks(dash_app=dash_app)

    @dash_app.callback(
        Output("content-pane", "children"),
        [Input("url", "pathname")]
    )
    def render_page_content(pathname):

        if pathname == '/dashapp/':
            return home_page.get_layout()
        if pathname == '/login':
            return login.get_layout()
        if pathname == '/register':
            return register.get_layout()
        elif pathname == "/map-view":
            return map_frame.get_layout()
        elif pathname == "/indices":
            return indices.get_indices_layout()
        elif pathname == "/google_trends":
            return google_trends.get_layout()
        # If the user tries to reach a different page, return a 404 message
        return dbc.Jumbotron(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ]
        )

        # @app.callback(
        #     Output('content-pane', 'children'),
        #     [
        #         Input("dash-container", "children"),
        #         # Input("button-open-sa-map", "n_clicks")
        #     ]
        # )
        # def get(a):
        #     trigger = get_callback_trigger(dash.callback_context)

        #     if trigger is None:
        #         return home_page.get_layout()
        #     elif trigger == 'button-open-retail-indices':
        #         return indices.get_indices_layout()
        #     elif trigger == 'button-open-sa-map':
        #         return map_frame.get_layout()

        # def filter_for_global_dropdowns(
        # df, year_month, industry, prices, actual_or_adjusted):

        #     if year_month:
