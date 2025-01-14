import functools
import itertools

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from flask import current_app as app
from flask.json import jsonify
from . import db
from . import modelling

bp = Blueprint('topics', __name__, url_prefix='/')


def read_text(limit=-1):
  '''Retreive corpus doc text from SQL tables.

  Limit controls the number of returned documents.
  If limit == -1 all rows are returned.
  '''
  df = db.read_all_cuisine_doc_text_to_dataframe(limit)
  return df


def yield_first_n(iterable):
    return [x for x in itertools.islice(iterable, 20)]


@bp.route('/topic/topic_main', methods=('GET', 'POST'))
def topics_all():
    '''Render a page listing all topics found in the corpus.

    Shows the top 30 topics in the corpus, and the 20 most 
    highly weighted words for each topic. Topics are generated
    by modelling.run_topic_model().
    '''
    if request.method == 'POST':
        error = "Post not implemented for /topic_main"
        flash(error)

    df = read_text()
    df["all_text"] = (df["document_name"] + df["description"] + df["steps"] +
                      df["tags"])
    #df["ingredients"])
    print("topic_main df {}".format(df))
    topic_model = modelling.run_topic_model(df, app.instance_path)
    print("Successfully ran topic model!")
    print("topic_model {}".format(topic_model))
    if g.dictionary:
        print("Dictionary keys l:{} {}\n Dictionary values l:{} {}\n".format(
            len(g.dictionary.keys()), yield_first_n(g.dictionary.keys()),
            len(g.dictionary.values()), yield_first_n(g.dictionary.values())))
        print("Dictionary token2id l:{} {}".format(
            len(g.dictionary.token2id), yield_first_n(g.dictionary.token2id)))
        print("Dictionary token2id keys {}".format(
            yield_first_n(g.dictionary.token2id.keys())))

    return render_template('topic/topic_main.html',
                           df=df,
                           topic_model=topic_model,
                           topics=topic_model.print_topics(
                               num_topics=modelling._NUM_TOPICS, num_words=20))


@bp.route('/topic/corpus', methods=('GET', 'POST'))
def corpus_main():
    '''Render a page displaying a sample of 20 random documents from
    the corpus.
    '''
    if request.method == 'POST':
        error = "Post not implemented for /corpus"
        flash(error)

    df = read_text(limit=1000)
    df["all_text"] = (df["document_name"] + df["description"] + df["steps"] +
                      df["tags"])
    # df["ingredients"])
    # topic_model = modelling.run_topic_model(df, app.instance_path)
    # print("Successfully ran topic model!")
    # print("topic_model {}".format(topic_model))
    data = {
        "n_docs": df.shape[0],
        "avg_doc_length": "{:.2f}".format(df["all_text"].str.len().mean()),
        # "num_topics": topic_model.get_topics().shape[0],
    }

    print("returning from corpus")
    return render_template('topic/corpus.html', data=data)


@bp.route('/topic/background_fetch_corpus_data', methods=('GET', ))
def background_fetch_corpus_data():
    '''Fetch a new set of 20 random documents from the corpus. 

    The `/topic/corpus` page is re-rendered with the new documents.
    The documents are returned as a serialized JSON payload.
    '''
    n_docs = request.args.get("n_docs", default=20)
    print(f"requesting {n_docs} docs")
    df = db.read_random_doc_text_to_dataframe(nrows=n_docs)
    text_df = df[[
        "document_name", "description", "steps", "ingredients", "tags"
    ]]
    print("background_fetch_corpus_data text df {}".format(text_df))
    return jsonify(text_df.to_dict('records'))
