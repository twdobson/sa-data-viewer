import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    # "padding": "2rem 1rem",
    "padding": "4rem 1rem 2rem",
    "background-color": "#f8f9fa",

}

submenu_1 = [
    html.Li(
        # use Row and Col components to position the chevrons
        dbc.Row(
            [
                dbc.Col("Stats SA"),
                dbc.Col(
                    html.I(className="fas fa-chevron-right mr-3"), width="auto"
                ),
            ],
            className="my-1",
        ),
        id="submenu-1",
    ),
    # we use the Collapse component to hide and reveal the navigation links
    dbc.Collapse(
        [
            dbc.NavLink("Indices", href="/indices"),
            dbc.NavLink("TBC", href="/tbc"),
        ],
        id="submenu-1-collapse",
    ),
]

submenu_2 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col("Census"),
                dbc.Col(
                    html.I(className="fas fa-chevron-right mr-3"), width="auto"
                ),
            ],
            className="my-1",
        ),
        id="submenu-2",
    ),
    dbc.Collapse(
        [
            dbc.NavLink("Map view", href="/map-view"),
            dbc.NavLink("TBC", href="/tbc"),
        ],
        id="submenu-2-collapse",
    ),
]

submenu_3 = [
    html.Li(
        # use Row and Col components to position the chevrons
        dbc.Row(
            [
                dbc.Col("Other data sources"),
                dbc.Col(
                    html.I(className="fas fa-chevron-right mr-3"), width="auto"
                ),
            ],
            className="my-1",
        ),
        id="submenu-3",
    ),
    # we use the Collapse component to hide and reveal the navigation links
    dbc.Collapse(
        [
            dbc.NavLink("Google trends", href="/google_trends"),
        ],
        id="submenu-3-collapse",
    ),
]

sidebar = html.Div(
    [
        html.H2("Nav", className="display-4"),
        html.Hr(),
        html.P(
            "Dashboard Views", className="lead"
        ),
        dbc.Nav(submenu_1 + submenu_2 + submenu_3, vertical=True),
    ],
    style=SIDEBAR_STYLE,
)


def init_callbacks(dash_app):
    # this function is used to toggle the is_open property of each Collapse
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    # this function applies the "open" class to rotate the chevron
    def set_navitem_class(is_open):
        if is_open:
            return "open"
        return ""

    for i in [1, 2, 3]:
        dash_app.callback(
            Output(f"submenu-{i}-collapse", "is_open"),
            [Input(f"submenu-{i}", "n_clicks")],
            [State(f"submenu-{i}-collapse", "is_open")],
        )(toggle_collapse)

        dash_app.callback(
            Output(f"submenu-{i}", "className"),
            [Input(f"submenu-{i}-collapse", "is_open")],
        )(set_navitem_class)
