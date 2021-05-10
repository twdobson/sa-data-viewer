import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash import no_update
from dash.dependencies import Input, Output, State

email_input = dbc.FormGroup(
    [
        dbc.Label("Email", html_for="input-login-email", width=2),
        dbc.Col(
            dbc.Input(
                type="email",
                id="input-login-email",
                placeholder="Enter email"
            ),
            width=10,
        ),
    ],
    row=True,
)

password_input = dbc.FormGroup(
    [
        dbc.Label("Password", html_for="input-login-password", width=2),
        dbc.Col(
            dbc.Input(
                type="password",
                id="input-login-password",
                placeholder="Enter password",
            ),
            width=10,
        ),
    ],
    row=True,
)


def get_layout():
    layout = [
        html.Br(),
        html.H2('Please login to continue'),
        dbc.Form([email_input, password_input]),
        html.Button('Login', id='button-login'),
        html.Hr(),
        html.P("Not registered?"),
        dcc.Link(html.Button('Register'), href='/register')
        # html.Button('Register Now!', id='button-register')
    ]

    return layout


# def login_button_click(n_clicks, username, password):
#     if n_clicks > 0:
#         if username == 'test' and password == 'test':
#             user = User(username)
#             login_user(user)
#             return '/success', ''
#         else:
#             return '/login', 'Incorrect   username or password'


def init_callbacks(dash_app):

    @dash_app.callback(
        Output('url', 'pathname'),
        Input('button-login', "n_clicks"),
        [
            State('input-login-email', 'value'),
            State('input-login-password', 'value')
        ]
    )
    def login(button_login_clicks, email, password):
        # trigger = get_callback_trigger(dash.callback_context)

        if button_login_clicks is not None:
            return '/'
        else:
            return no_update
