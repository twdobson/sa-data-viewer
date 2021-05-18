# import dash_bootstrap_components as dbc
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output, State

# email_input = dbc.FormGroup(
#     [
#         dbc.Label("Email", html_for="input-register-email", width=2),
#         dbc.Col(
#             dbc.Input(
#                 type="email",
#                 id="input-register-email",
#                 placeholder="Enter email"
#             ),
#             width=10,
#         ),
#     ],
#     row=True,
# )

# password_input = dbc.FormGroup(
#     [
#         dbc.Label("Password", html_for="input-register-password", width=2),
#         dbc.Col(
#             dbc.Input(
#                 type="password",
#                 id="input-register-password",
#                 placeholder="Enter password",
#             ),
#             width=10,
#         )
#     ],
#     row=True,
# )

# confirm_password_input = dbc.FormGroup(
#     [
#         dbc.Label(
#             "Repeat Password",
#             html_for="input-register-password-repeat",
#             width=2
#         ),
#         dbc.Col(
#             dbc.Input(
#                 type="password",
#                 id="input-register-password-repeat",
#                 placeholder="Enter password",
#             ),
#             width=10,
#         ),
#     ],
#     row=True,
# )


# def get_layout():
#     layout = [
#         html.Br(),
#         html.H2('Please register'),
#         dbc.Form([email_input, password_input, confirm_password_input]),
#         html.Button('Login', id='button-login'),
#         html.Hr(),
#         html.P("Not registered?"),
#         dcc.Link(html.Button('Register'), href='/register')
#     ]

#     return layout


# def init_callbacks(dash_app):

#     @dash_app.callback(
#         Output('url', 'pathname'),
#         Input('button-login', "n_clicks"),
#         [
#             State('input-login-email', 'value'),
#             State('input-login-password', 'value'),
#             State('input-login-password-repeat', 'value')
#         ]
#     )
#     def register(button_login_clicks, email, password, password_repeat):
#         # trigger = get_callback_trigger(dash.callback_context)

#         # if button_login_clicks is not None:
