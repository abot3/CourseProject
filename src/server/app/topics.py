import functools

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from flask import current_app as app
from . import db
from . import modelling

bp = Blueprint('topics', __name__, url_prefix='/')


@bp.route('/topic/topic_main', methods=('GET', 'POST'))
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
    df["all_text"] = (df["document_name"] + df["description"] + df["steps"] +
                      df["ingredients"])  # + df["tags"])
    print("topic_main df {}".format(df))
    topic_model = modelling.run_topic_model(df, app.instance_path)
    print("Successfully ran topic model!")
    print("topic_model {}".format(topic_model))

    return render_template('topic/topic_main.html', df=df, topic_model=topic_model)


@bp.route('/topic/corpus', methods=('GET', 'POST'))
def corpus_main():
    if request.method == 'POST':
        # username = request.form['username']
        # password = request.form['password']
        # db = get_db()
        error = "Post not implemented for /corpus"

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
    df["all_text"] = (df["document_name"] + df["description"] + df["steps"] +
                      df["ingredients"])  # + df["tags"])
    print("topic_main df {}".format(df))
    topic_model = modelling.run_topic_model(df, app.instance_path)
    print("Successfully ran topic model!")
    print("topic_model {}".format(topic_model))
    data = {
        "n_docs" : df.shape[0],
        "avg_doc_length": "{:.2f}".format(df["all_text"].str.len().mean()),
        "num_topics": topic_model.get_topics().shape[0],
    }

    print("returning from corpus")
    return render_template('topic/corpus.html', data=data)

@bp.route('/topic/background_fetch_corpus_data', methods=('GET',))
def background_fetch_corpus_data():
    df = db.read_random_doc_text_to_dataframe(nrows=20)
    # df["all_text"] = (df["document_name"] + df["description"] + df["steps"] +
    #                   df["ingredients"] + df["tags"])
    text_df = df["document_name", "description", "steps", "ingredients", "tags"]
    print("background_fetch_corpus_data text df {}".format(text_df))
    return jsonify(text_df.to_dict('records'))
































