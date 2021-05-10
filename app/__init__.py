import os
from flask import Flask
from app.config import config
from app.dash_app.dashboard import init_dash_app

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


def create_app(config_class=None):
    app = Flask(__name__)

    env = os.environ.get("FLASK_ENV", "dev")
    app.config.from_object(config[env])

    # register sqlalchemy to this app
    from app.models import db
    db.init_app(app)

    from app.models import login_manager
    login_manager.init_app(app)

    # init dash apps
    app = init_dash_app(app)

    return app


# def register_dashapp(app, title, base_pathname, layout, register_callbacks_fun):
#     # Meta tags for viewport responsiveness
#     meta_viewport = {
#         "name": "viewport",
#         "content": "width=device-width, initial-scale=1, shrink-to-fit=no"
#     }

#     my_dashapp = dash.Dash(__name__,
#                            server=app,
#                            url_base_pathname=f'/{base_pathname}/',
#                            assets_folder=get_root_path(__name__) + f'/{base_pathname}/assets/',
#                            meta_tags=[meta_viewport])
#     # Push an application context so we can use Flask's 'current_app'
#     with app.app_context():
#         my_dashapp.title = title
#         my_dashapp.layout = layout
#         register_callbacks_fun(my_dashapp)
#     _protect_dashviews(my_dashapp)
