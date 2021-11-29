import os
from typing import Optional, List, Tuple

import pandas as pd
from gensim.models.ldamulticore import LdaMulticore
from gensim.parsing import preprocessing
from gensim.corpora import Dictionary
# from nltk.stem.wordnet import WordNetLemmatizer
from gensim.parsing.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer

_MODEL_NAME = "lda_model.model"
_NUM_TOPICS = 20
_NUM_WORKDERS = 4
_DOC_CHUNKSIZE = 500
_DF_ROW_FRACTION = 0.05


def try_get_saved_model(instance_path: str) -> Optional[LdaMulticore]:
    model = None
    path = os.path.join(instance_path, _MODEL_NAME)
    if not os.path.exists(path):
        raise IOError(f"Could not locate path {path}")
    try:
        model = LdaMulticore.load(path)
    except Exception as e:
        pass
    return model


def try_save_model(instance_path: str, model: LdaMulticore):
    path = os.path.join(instance_path, _MODEL_NAME)
    print("saving to {}".format(path))
    if not model:
        raise ValueError("Cannot save null model")
    if not os.path.exists(instance_path):
        raise IOError(f"Could not locate path {instance_path}")
    model.save(path)


def build_gensim_corpus(
        df: pd.DataFrame) -> Tuple[List[Tuple[int, int]], Dictionary]:
    docs = df["all_text"].sample(frac=_DF_ROW_FRACTION).to_numpy()

    # Split the documents into tokens.
    tokenizer = RegexpTokenizer(r'\w+')
    p = PorterStemmer()
    for idx in range(len(docs)):
        docs[idx] = preprocessing.remove_stopwords(docs[idx])
        docs[idx] = preprocessing.preprocess_string(
            docs[idx],
            filters=[
                preprocessing.strip_tags, preprocessing.strip_punctuation,
                preprocessing.strip_multiple_whitespaces,
                preprocessing.strip_numeric, preprocessing.strip_short
            ])
        docs[idx] = ' '.join(docs[idx])
        docs[idx] = docs[idx].lower()  # Convert to lowercase.
        docs[idx] = p.stem_sentence(docs[idx])
        docs[idx] = tokenizer.tokenize(docs[idx])  # Split into words.

    # Remove numbers, but not words that contain numbers.
    docs = [[token for token in doc if not token.isnumeric()] for doc in docs]
    # Remove words that are only one character.
    docs = [[token for token in doc if len(token) > 1] for doc in docs]

    # Lemmatize the documents. This is better than Porter stemmer but
    # requires auto install of nltk data.
    # lemmatizer = WordNetLemmatizer()
    # docs = [[lemmatizer.lemmatize(token) for token in doc] for doc in docs]
    # docs = [[p.stem_sentence(token) for token in doc] for doc in docs]

    # Create a dictionary representation of the documents.
    dictionary = Dictionary(docs)
    print("docs\n{}".format(docs[1:20]))
    # Filter out words that occur less than 20 documents, or more than 50% of the documents.
    dictionary.filter_extremes(no_below=2, no_above=0.2)

    # Bag-of-words representation of the documents.
    # Convert document into the bag-of-words (BoW) format
    # = list of (token_id, token_count) tuples.
    corpus = [dictionary.doc2bow(doc) for doc in docs]
    print('Number of unique tokens: %d' % len(dictionary))
    print('Number of documents: %d' % len(corpus))
    return (corpus, dictionary)


def compute_lda_model(df: pd.DataFrame):
    corpus, dictionary = build_gensim_corpus(df)
    # https://stackoverflow.com/questions/67229373/gensim-lda-error-cannot-compute-lda-over-an-empty-collection-no-terms
    temp = dictionary[0]  # This is only to "load" the dictionary.
    model = LdaMulticore(corpus,
                         id2word=dictionary.id2token,
                         eta='auto',
                         num_topics=_NUM_TOPICS,
                         eval_every=None)
    return model


def run_topic_model(df: pd.DataFrame, instance_path: str) -> LdaMulticore:
    model = None
    try:
        model = try_get_saved_model(instance_path)
        print("Model topics {}".format(model.print_topics(num_topics=_NUM_TOPICS, num_words=20)))
        return model
    except IOError as e:
        pass

    model = compute_lda_model(df)
    print("Model topics {}".format(model.print_topics(num_topics=_NUM_TOPICS, num_words=20)))
    try_save_model(instance_path, model)
    return model
