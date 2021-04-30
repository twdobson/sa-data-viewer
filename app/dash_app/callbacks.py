from dash.dependencies import Input, Output

from app.models import db, MonthlyTimeSeries
from manage import app


@app.callback(
    Output('text-out', "children"),
    Input('button-button', 'nclicks')
)
def add_button(nclicks):
    print(nclicks)
    if nclicks:
        monthly_time_series = MonthlyTimeSeries(
            industry='new',
            year_month=202001,
            index=1111,
        )

        db.session.add(monthly_time_series)
        db.session.commit()

    q = MonthlyTimeSeries.query().all()
    return q if q is not None else "ERROR"
