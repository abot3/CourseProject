import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from . import db
from . import modelling

bp = Blueprint('topics', __name__, url_prefix='/')


@bp.route('/topic_main', methods=('GET', 'POST'))
def topics_all():
    if request.method == 'POST':
        # username = request.form['username']
        # password = request.form['password']
        # db = get_db()
        error = "Post not implemented for /topic_main"

        # if not username:
        #     error = 'Username is required.'
        # elif not password:
        #     error = 'Password is required.'

        # if error is None:
        #     try:
        #         db.execute(
        #             "INSERT INTO user (username, password) VALUES (?, ?)",
        #             (username, generate_password_hash(password)),
        #         )
        #         db.commit()
        #     except db.IntegrityError:
        #         error = f"User {username} is already registered."
        #     else:
        #         return redirect(url_for("auth.login"))

        flash(error)

    df = db.read_all_doc_text_to_dataframe()
    topic_model = modelling.run_topic_model(df)
    print("topic_main df {}".format(df))

    return render_template('topics/topic_main.html', df=df)

