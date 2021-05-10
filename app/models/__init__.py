# this file structure follows http://flask.pocoo.org/docs/1.0/patterns/appfactories/
# initializing db in api.models.base instead of in api.__init__.py
# to prevent circular dependencies
from .base import db, login_manager
from .geospatial import Province
from .models import RetailMonthlyTimeSeries, RetailSeries
from .user import User

__all__ = [
    "RetailMonthlyTimeSeries",
    "RetailSeries",
    'Province',
    "db",
    'User'
]
