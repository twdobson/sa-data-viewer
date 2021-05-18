# this file structure follows http://flask.pocoo.org/docs/1.0/patterns/appfactories/
# initializing db in api.models.base instead of in api.__init__.py
# to prevent circular dependencies
from app.extensions import db
from .geospatial import Province
from .models import RetailMonthlyTimeSeries, RetailSeries
from .user import User
from .google_trends import GoogleTrends

__all__ = [
    "RetailMonthlyTimeSeries",
    "RetailSeries",
    'Province',
    "db",
    'User',
    'GoogleTrends'
]
