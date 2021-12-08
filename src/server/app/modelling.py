import os
import pickle
from typing import Optional, List, Tuple
from datetime import datetime

import pandas as pd
import numpy as np
from gensim.models.ldamulticore import LdaMulticore
from gensim.parsing import preprocessing
from gensim.corpora import Dictionary
from flask import g
from gensim.parsing.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
import logging

logging.basicConfig(filename='gensim.log',
                    format="%(asctime)s:%(levelname)s:%(message)s",
                    level=logging.INFO)

# Output filenames. Used to cache corpus and model on disk.
_MODEL_NAME = "lda_model.model"
_DICTIONARY_NAME = "dictionary.corpus"
_CORPUS_NAME = "corpus.corpus"
# Number of topics to generate via the topic model.
_NUM_TOPICS = 30
# Max iterations and epochs to run the topic model.
_NUM_PASSES = 10
_NUM_ITERATIONS = 100
_EVAL_EVERY = 1
# Number of parallel processes used when generating topic model
_NUM_WORKDERS = 3
# Max number of docs to hold in memory per worker.
_DOC_CHUNKSIZE = 2000
# % of docs from corpus used to generate topic model.
# Lowing this number decreses runtime significantly.
_DF_ROW_FRACTION = 1.0
# All Latent Dirichlet Allocation prior probabilities must sum
# to 1. Reserve 20% probability for key words corresponding to
# the user's desired topics. A list of keywords is stored in
# _LDA_KEYWORD_PRIORS.
_PRIOR_PROBABILITY = 0.2
_LDA_KEYWORD_PRIORS = [
    "chines",
    "korea",
    "korean",
    "viet",
    "vietnames",
    "vietnam",
    "singapore",
    "singaporean",
    "italy",
    "italian",
    "italyi",
    "european",
    "french",
    "mexican",
    "mexico",
    "france",
    "british",
    "britain",
    "mediterranean",
    "africa",
    "african",
    "kenya",
    "kenyan"
    "israel",
    "israeli",
    "middle-east",
    "middleeast",
    "india",
    "halal",
    "arab",
    "arabian",
    "egyptian",
    "egypt",
    "japan",
    "japanese",
    "german",
    "american",
    "america",
]


def try_get_saved_model(instance_path: str) -> Optional[LdaMulticore]:
    '''If path exists deserialize the model from disk to memory.

    Model generation can take minutes. Saving the model to disk and
    reading it back when required is much faster than regenerating.
    '''
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
    '''If path exists serialize the model to a file on disk.

    Model generation can take minutes. Saving the model to disk and
    reading it back when required is much faster than regenerating.
    '''
    path = os.path.join(instance_path, _MODEL_NAME)
    print("saving to {}".format(path))
    if not model:
        raise ValueError("Cannot save null model")
    if not os.path.exists(instance_path):
        raise IOError(f"Could not locate path {instance_path}")
    model.save(path)


def try_get_saved_dictionary(instance_path: str) -> Optional[Dictionary]:
    '''If path exists deserialize the tokenized bag-of-words dictionary from disk.

    Tokenizing, stemming, and storing the dictionary is much slower than
    loading it from disk.
    Uses the pickle module for serialization.
    '''
    model = None
    path = os.path.join(instance_path, _DICTIONARY_NAME)
    if not os.path.exists(path):
        raise IOError(f"Could not locate path {path}")
    try:
        dictionary = Dictionary.load(path)
    except Exception as e:
        pass
    return dictionary


def try_save_dictionary(instance_path: str, dictionary: Dictionary):
    '''If path exists serialize the tokenized bag-of-words dictionary to disk.

    Tokenizing, stemming, and storing the dictionary is much slower than
    loading it from disk.
    Uses the pickle module for serialization
    '''
    path = os.path.join(instance_path, _DICTIONARY_NAME)
    print("saving dictionary to {}".format(path))
    if not dictionary:
        raise ValueError("Cannot save null dictionary")
    if not os.path.exists(instance_path):
        raise IOError(f"Could not locate path {instance_path}")
    dictionary.save(path)


def try_get_saved_corpus(
        instance_path: str) -> Optional[List[Tuple[int, int]]]:
    '''If path exists deserialize the corpus of text documents from disk.

    Querying the SQL databse and re-cleaning the document text takes about
    as long as just deserializing the existing corpus from disk.
    Uses the pickle module for serialization.
    '''
    corpus = None
    path = os.path.join(instance_path, _CORPUS_NAME)
    if not os.path.exists(path):
        raise IOError(f"Could not locate path {path}")
    try:
        with open(path, 'rb') as input:
            corpus = pickle.load(input)
    except Exception as e:
        pass
    return corpus


def try_save_corpus(instance_path: str, corpus: List[Tuple[int, int]]):
    '''If path exists deserialize the corpus of text documents from disk.

    Querying the SQL databse and re-cleaning the document text takes about
    as long as just deserializing the existing corpus from disk.
    Uses the pickle module for serialization.
    '''
    path = os.path.join(instance_path, _CORPUS_NAME)
    print("saving corpus to {}".format(path))
    if not corpus:
        raise ValueError("Cannot save null corpus")
    if not os.path.exists(instance_path):
        raise IOError(f"Could not locate path {instance_path}")
    with open(path, 'wb') as out:
        pickle.dump(corpus, out)


def build_gensim_corpus(
        df: pd.DataFrame) -> Tuple[List[Tuple[int, int]], Dictionary]:
    docs = df["all_text"].sample(frac=_DF_ROW_FRACTION).to_numpy()
    '''Build a bag-of-words representation of the corpus. 

    Remove numerics, and invalid characters, tokenize, and stem the words
    in the corpus.
    Remove any stopwords from the text.
    Remove any tokens that occur in > 40% of documents.
    '''

    # Split the documents into tokens.
    tokenizer = RegexpTokenizer(r'\w+')
    p = PorterStemmer()
    for idx in range(len(docs)):
        docs[idx] = preprocessing.preprocess_string(
            docs[idx],
            filters=[
                preprocessing.strip_tags, preprocessing.strip_punctuation,
                preprocessing.strip_multiple_whitespaces,
                preprocessing.strip_numeric, preprocessing.strip_short
            ])
        docs[idx] = ' '.join(docs[idx])
        docs[idx] = docs[idx].lower()  # Convert to lowercase.
        docs[idx] = preprocessing.remove_stopwords(docs[idx])
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
    # Filter out words that occur less than 0 documents, or more than 40% of the documents.
    dictionary.filter_extremes(no_below=0, no_above=0.4)

    # Bag-of-words representation of the documents.
    # Convert document into the bag-of-words (BoW) format
    # = list of (token_id, token_count) tuples.
    corpus = [dictionary.doc2bow(doc) for doc in docs]
    return (corpus, dictionary)


def print_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)


def create_eta():
    '''Create numpy array of dirichlet priors.

    Where N is the number of unique tokens in the corpus. Create a
    numpy array with length N. Each entry corresponds to the Dirichlet
    prior for a single word. Set the probability of each word to 1/N
    initially.

    For key words that correspond to topics of interest increase the
    probability to be > 1/N while keeping sum(ARR) = 1.0.

    Returns the modified numpy array
    '''
    global _LDA_KEYWORD_PRIORS
    dictionary = g.dictionary
    corpus = g.corpus
    culture_match_ids = list()
    all_tokens = dictionary.token2id.keys()
    print("Dictionary is {}".format(g.dictionary))
    print("Dictionary repr is {}".format(repr(g.dictionary)))
    print("Dictionary token2id is {}".format(repr(g.dictionary.token2id)))
    print("korea in Dictionary token2id is {}".format(
        g.dictionary.token2id["korea"]))
    for culture in _LDA_KEYWORD_PRIORS:
        print("Searching for {}, in {}".format(
            culture, dictionary.token2id.get(culture, "<blank>")))
        if culture in dictionary.token2id:
            print(f"Found culture {culture} in tokens")
            culture_match_ids.append((culture, dictionary.token2id[culture]))
    n_tokens = len(all_tokens)
    n_culture_tokens = len(culture_match_ids)
    n_normal_tokens = n_tokens - n_culture_tokens
    print(f"{n_tokens}, {n_culture_tokens}, {n_normal_tokens}")
    per_token_probability = (1.0 - _PRIOR_PROBABILITY) / n_normal_tokens
    culture_token_probability = (_PRIOR_PROBABILITY) / n_culture_tokens
    eta = list(np.full(n_tokens, per_token_probability))
    for culture in culture_match_ids:
        eta[culture[1]] = culture_token_probability
    return eta


def compute_lda_model(df: pd.DataFrame, instance_path: str):
    '''Load the corpus and bag-of-words dictionary from disk. Compute topic model.

    Returns the top 20 words and _NUM_TOPICS most significant topics discovered
    by the topic modeling algorithm.
    '''
    print_time()
    corpus, dictionary = build_gensim_corpus(df)
    # https://stackoverflow.com/questions/67229373/gensim-lda-error-cannot-compute-lda-over-an-empty-collection-no-terms
    print_time()
    temp = dictionary[0]  # This is only to "load" the dictionary.
    print_time()
    try_save_dictionary(instance_path, dictionary)
    print_time()
    try_save_corpus(instance_path, corpus)
    print_time()
    g.dictionary = dictionary
    g.corpus = corpus
    eta = create_eta()
    model = LdaMulticore(
        corpus,
        workers=_NUM_WORKDERS,
        id2word=dictionary.id2token,
        # eta='auto',
        eta=eta,
        num_topics=_NUM_TOPICS,
        passes=_NUM_PASSES,
        iterations=_NUM_ITERATIONS,
        eval_every=_EVAL_EVERY)
    print_time()
    return model


def run_topic_model(df: pd.DataFrame, instance_path: str) -> LdaMulticore:
    '''Return top _NUM_TOPICS topcs in the corpus using and LDA model.

    Main method for the generating topics used by the `/topic/corpus`
    view.
    '''
    model = None
    try:
        dictionary = try_get_saved_dictionary(instance_path)
        corpus = try_get_saved_corpus(instance_path)
        g.dictionary = dictionary
        g.corpus = corpus
    except IOError as e:
        pass

    try:
        model = try_get_saved_model(instance_path)
        print("Model topics {}".format(
            model.print_topics(num_topics=_NUM_TOPICS, num_words=20)))
        return model
    except IOError as e:
        pass

    model = compute_lda_model(df, instance_path)
    print("Model topics {}".format(
        model.print_topics(num_topics=_NUM_TOPICS, num_words=20)))
    try_save_model(instance_path, model)
    return model
