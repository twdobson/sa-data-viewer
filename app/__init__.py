import os
from flask import Flask
from app.config import config
# from app.dash_app.dashboard import init_dash_app
import dash
from flask.helpers import get_root_path
import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


def create_app(config_class=None):
    app = Flask(__name__)

    env = os.environ.get("FLASK_ENV", "dev")
    app.config.from_object(config[env])

    from app.dashapp import dashboard
    # from app.dashapp1.callbacks import register_callbacks as register_callbacks1
    register_dashapp(
        app,
        'Dashapp 1',
        'dashapp',
        dashboard.layout,
        dashboard.init_callbacks
    )

    register_extensions(app)
    register_blueprints(app)

    # init dash apps
    # app = init_dash_app(app)

    return app


def register_extensions(app):
    from app.extensions import db
    from app.extensions import login_manager
    # from app.extensions import migrate

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    # migrate.init_app(app, db)


def register_blueprints(app):
    from app.webapp import server_bp

    app.register_blueprint(server_bp)


def register_dashapp(app, title, base_pathname, layout, register_callbacks_fun):
    # Meta tags for viewport responsiveness
    meta_viewport = {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1, shrink-to-fit=no"
    }

    FA = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"

    my_dashapp = dash.Dash(
        __name__,
        server=app,
        url_base_pathname=f'/{base_pathname}/',
        assets_folder=get_root_path(__name__) + f'/{base_pathname}/assets/',
        # assets_folder=get_root_path(__name__) + 'app/assets/',
        meta_tags=[meta_viewport],
        external_stylesheets=[dbc.themes.BOOTSTRAP, FA]
    )
    # Push an application context so we can use Flask's 'current_app'
    with app.app_context():
        my_dashapp.title = title
        my_dashapp.layout = layout
        register_callbacks_fun(my_dashapp)
    # _protect_dashviews(my_dashapp)
