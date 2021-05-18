from app.extensions import db


class RetailSeries(db.Model):
    __tablename__ = "RetailSeries"

    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    label = db.Column(db.String(64))
    split = db.Column(db.String(64))
    industry = db.Column(db.String(255))
    prices = db.Column(db.String(64))
    actual_or_adjusted = db.Column(db.String(64))

    label = db.relationship(
        'RetailMonthlyTimeSeries',
        backref='series_information',
        lazy='dynamic'
    )


class RetailMonthlyTimeSeries(db.Model):
    __tablename__ = "RetailMonthlyTimeSeries"

    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    retail_series_id = db.Column(db.Integer, db.ForeignKey('RetailSeries.id'))
    year_month = db.Column(db.Integer, primary_key=True)
    spend = db.Column(db.Numeric)
