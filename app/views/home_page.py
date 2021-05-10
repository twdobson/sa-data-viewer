import dash_html_components as html
from app.views.components import sidebar

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


def get_layout():
    layout = [
        sidebar,
        html.Div(
            html.P(
                id='paragraph-introduction text',
                children="Welcome to data viewer homepage"
            ),
            style=CONTENT_STYLE
        )
    ]

    return layout
