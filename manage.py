from flask_migrate import MigrateCommand
from flask_script import Manager

from app import create_app
from app.models import db

# sets up the app
app = create_app()

manager = Manager(app)
manager.add_command("db", MigrateCommand)


@manager.command
def runserver():
    app.run(debug=True, host="0.0.0.0", port=5000)


@manager.command
def runworker():
    app.run(debug=False)


@manager.command
def recreate_db():
    """
    Recreates a database. This should only be used once
    when there's a new database instance. This shouldn't be
    used when you migrate your database.
    """
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == "__main__":
    manager.run()
