from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# instantiate database object
db = SQLAlchemy()
login_manager = LoginManager()
