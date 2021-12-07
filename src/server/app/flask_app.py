import os

from flask import (Flask, render_template)
from . import db
from . import topics


def DoDbSetup(app):
    db.init_app(app)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    print(f"Instance path is `{app.instance_path}`")
    print(f"__name__ path is `{__name__}`")
    print(f"app.root path is `{app.root_path}`")
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # Take care of DB related setup items.
    DoDbSetup(app)

    # Ensure the instance folder exists.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # A simple page that says hello.
    @app.route('/')
    @app.route('/index')
    def index():
        return render_template('index.html')

    # Register any additional pages.
    app.register_blueprint(topics.bp)

    return app
