from app.extensions import db


class GoogleTrends(db.Model):
    __tablename__ = "GoogleTrends"

    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime(timezone=True))
    search_term = db.Column(db.String(64))
    week_start_date = db.Column(db.Date)
    trend_index = db.Column(db.Numeric)
