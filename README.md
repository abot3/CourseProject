# Table of Contents

1. [Overview](#overview)
2. [Implementation](#implementation)
3. [Usage](#usage)
4. [Contributors](#contributors)

# Course Project

Please fork this repository and paste the github link of your fork on Microsoft CMT. Detailed instructions are on Coursera under Week 1: Course Project Overview/Week 9 Activities.

## Note to Reviewers

The project video and `app.sqlite` is available on Google Drive here:
https://drive.google.com/drive/folders/17Mq_xarb6h1H-DZeqW3I513ew_QwB5fR?usp=sharing.

Please copy the `app.sqlite` to `/CourseProject/src/server/instance/`. This will allow you
to skip setting up the DB (`flask init-db`) which can take a few minutes.

# 1) Overview <a name="overview"></a>

As stated in the project proposal the purpose of this code is to provide an implementation
of topic modeling for a commonly used web server. With the popularity of 
user-generated content on today's websites it's important for smaller sites to be able to
interpret and discover topics or clusters within their text data. 

### Functionality: What It Does  

An example app was developed using the Flask webserver.
Flask was chosen for its popularity, simplicity, and due to it being written in Python.
This project also makes use of Pandas, Numpy,
and Gensim libraries for building the data cleaning, and building the topic model. All these libraries are
written in Python, so installation and integration with the server is straightforward.

The example app contains data cleaning, topic modeling, and storage functions that can be
re-used by any Flask app. However, much of the code is currently tied to the specific dataset used
by the example app, a corpus of cooking recipes from `food.com`. There was not enough time to both
implement the web frontend and make the topic modeling backend generic.
Future work could focus on decoupling the strings and keywords specific to the `food.com` dataset from the generic 
topic modeling and storage functions. The generic code can be factored out into a
Flask plugin. Currently the demo app acts as a proof of concept rather than a fully independent
plugin.

### Functionality: What It Can Be Used For

The proof-of-concept app ingests a corpus of [cooking recipe data](https://www.kaggle.com/shuyangli94/food-com-recipes-and-user-interactions?select=RAW_recipes.csv) retrieved from Kaggle. The raw data contains
~230,000 unique recipes with the text fields `name, description, steps(preparation), tags(categories), and description`.
The data is in `.csv` format and is cleaned, deduplicated, tokenized, stemmed using Panda and Gensim 
(see `csv_ingest.py`, `db.py`). The cleaned dataset is then inserted in to a SQL (sqlite) database,
allowing simple analysis and easy keyword filtering (see `sql_strings.py`, `schema.sql`). Post filtering
a SQL query is run, retrieving ~120k rows from the database. The 120k rows are fed to the topic model
and the results are rendered in the web app.

Latent Dirichlet Allocation (LDA) was chosen as the topic model for the demo.
LDA was chosen instead of PLSA due to the nature of the demo dataset and becuase it allows for
Bayesian priors to be introduced into the model. The priors are essential to allow end-users to direct the topic modeling algorithm
to focus on a subset of keywords, representing the core topics the user would like the 
topic model to focus on. This allows the topic modeling algorithm to act as both an unsupervised
algorithm when priors are set to a uniform distribution over the corpus vocabulary, or similar 
to a text clustering algorithm if the user chooses to provide priors. The example app attempts to generate
~30 topics, with the hope that the majority of the topics map 1-to-1 to a specific type of cuisine
e.g. French, or Japanese. Indeed a significant increase in correlation of the topics with a specific cuisine
type was noticed when Dirichlet priors were set to a non-uniform distribution with high probability
assigned to keywords associated with cuisines of interest. This illustrates the usefulness of LDA
for end-users who would like directed topic modeling that can cluster documents to a set of roughly
known topics.


# 2) Implementation <a name="implementation"></a>

Per function documentation is available in the source code. This section will cover the two major
pages in the demo app. The GET request for each view is handled in `server/app/topics.py`:

1. Corpus View: `@bp.route('/topic/corpus', methods=('GET', 'POST'))`
2. Topic View: `@bp.route('/topic/topic_main', methods=('GET', 'POST'))`

#### Corpus View

```
This view reads all documents from the SQL database, creates the corpus
and BOW dictionary. 20 Documents are randomly selected from the corpus
and rendered in a table for inspection by the user.

Request call tree:

def corpus_main():
  '''Render a page displaying a sample of 20 random documents from
  the corpus.
  '''
|
| def read_text(limit=-1):
| | '''Retreive corpus doc text from SQL tables.

| | Limit controls the number of returned documents.
| | If limit == -1 all rows are returned.
| | '''
| | df = db.read_all_cuisine_doc_text_to_dataframe(limit)
| |
| |
| | 
| | def read_all_cuisine_doc_text_to_dataframe(limit=-1) -> pd.DataFrame:
| | | '''Retreive corpus doc text from SQL tables. Only return rows
| | | containing keywords related to cuisines of interest.
| | |
| | | Return a Pandas dataframe containing 1 row per document.
| | | '''
| | |
| | | # Reads all documents from SQL database.
| | | pd.read_sql(sql_strings._SELECT_ALL_CUISINE_TEXT_DATA_WITH_LIMIT)
| |   
| return render_template('topic/corpus.html', data=data)
```

This presents the main corpus view page to the user. If the click the 
`Display random corpus data` button an AJAX request is set to the server.
This request is to the following url. The handler queries 20 random docs
from the SQL databse and returns them as JSON and displayed via DOM updates.

```
@bp.route('/topic/background_fetch_corpus_data', methods=('GET', ))
def background_fetch_corpus_data():
  '''Fetch a new set of 20 random documents from the corpus. 

  The `/topic/corpus` page is re-rendered with the new documents.
  The documents are returned as a serialized JSON payload.
  '''
  | def read_random_doc_text_to_dataframe(nrows=10) -> pd.DataFrame:
  |     '''Retreive corpus doc text from SQL tables.

  |   Select random documents from corpus using SQL.
  |   Limit the number of rows returned to nrows.

  |   Return a Pandas dataframe containing 1 row per document.
  |   '''
  |   |
  |   |  df = pd.read_sql(sql_strings._SELECT_RANDOM_TEXT_DATA,
  |   |                    db,
  |   |                    params=[nrows],
  |   |                    index_col=None)
  |
  | return jsonify(text_df.to_dict('records'))
```

#### Topic View 

This view displays the top 30 topics discovered in the corpus. Each topic
is represented by a rank (displayed in descending order), and a list of the
20 most significant words in the topic.

This view is very slow to render. Internally it either creates the corpus or
loads a cached corpus from disk. The corpus is fed into the LDA topic model, which
can take many iterations to converge. If the model has already been computed it's
loaded from disk instead.

Request call tree:

```
@bp.route('/topic/topic_main', methods=('GET', 'POST'))
def topics_all():
  '''Render a page listing all topics found in the corpus.

  Shows the top 30 topics in the corpus, and the 20 most 
  highly weighted words for each topic. Topics are generated
  by modelling.run_topic_model().
  '''
  | 
  | def read_text(limit=-1):
  |   '''Retreive corpus doc text from SQL tables.
  |
  |   Limit controls the number of returned documents.
  |   If limit == -1 all rows are returned.
  |   '''
  |   df = db.read_all_cuisine_doc_text_to_dataframe(limit)
  |
  |   def read_all_cuisine_doc_text_to_dataframe(limit=-1) -> pd.DataFrame:
  |   |  '''Retreive corpus doc text from SQL tables. Only return rows
  |   |  containing keywords related to cuisines of interest.
  |   |
  |   |  Return a Pandas dataframe containing 1 row per document.
  |   |  '''
  |   |
  | topic_model = modelling.run_topic_model(df, app.instance_path)
  |
  |   def run_topic_model(df: pd.DataFrame, instance_path: str) -> LdaMulticore:
  |   |  '''Return top _NUM_TOPICS topcs in the corpus using and LDA model.

  |   |  Main method for the generating topics used by the `/topic/corpus`
  |   |  view.
  |   |  '''
  |   |  dictionary = try_get_saved_dictionary(instance_path)
  |   |  corpus = try_get_saved_corpus(instance_path)
  |   |  model = compute_lda_model(df, instance_path)
  |   |
  |   |    def compute_lda_model(df: pd.DataFrame, instance_path: str):
  |   |    |  '''Load the corpus and bag-of-words dictionary from disk. Compute topic model.
  |   |    |  
  |   |    |  Returns the top 20 words and _NUM_TOPICS most significant topics discovered
  |   |    |  by the topic modeling algorithm.
  |   |    |  '''
  |   |    |
  |   |    |  corpus, dictionary = build_gensim_corpus(df)
  |   |    |  eta = create_eta()
  |   |    |  |  def create_eta():
  |   |    |  |    '''Create numpy array of dirichlet priors.
  |   |    |  |    
  |   |    |  |    Where N is the number of unique tokens in the corpus. Create a
  |   |    |  |    numpy array with length N. Each entry corresponds to the Dirichlet
  |   |    |  |    prior for a single word. Set the probability of each word to 1/N
  |   |    |  |    initially.
  |   |    |  |    
  |   |    |  |    For key words that correspond to topics of interest increase the
  |   |    |  |    probability to be > 1/N while keeping sum(ARR) = 1.0.
  |   |    |  |    
  |   |    |  |    Returns the modified numpy array
  |   |    |  |    '''
  |   |    |  |
  |   |    |  model = LdaMulticore(
  |   |    |          corpus,
  |   |    |          workers=_NUM_WORKDERS,
  |   |    |          id2word=dictionary.id2token,
  |   |    |          # eta='auto',
  |   |    |          eta=eta,
  |   |    |          num_topics=_NUM_TOPICS,
  |   |    |          passes=_NUM_PASSES,
  |   |    |          iterations=_NUM_ITERATIONS,
  |   |    |          eval_every=_EVAL_EVERY)
  |   | return model
  |   return model
  | return render_template('topic/topic_main.html',
                           topic_model=topic_model,
```
## Project Layout

All server code is in the `server/app/*` directory. The `server/app/instance` folder
is for temporary instance data generated while the server is running. This is where
the database and models are stored.


```
│   README.md
│   install.sh
│   ...
server/app
│   
│   setup.py
│
└───src
│   │   flask_app.py
│   │   csv_ingest.py
│   │   db.py
│   │   topics.py
│   │   modelling.py
│   │   schema.sql
│   │   sql_strings.py
│   │
│   └───templates
│   │
│   │   │   corpus.html
│   │   │   topic_main.html
│   │   │   base.html
│   │   │   ...
│
│   └───static
│       │   style.css
│       │   ...
│   
└───instance
    │   *.sqlite
    │   *.model
    │   *.corpus
```


## Other Significant Functions

<br/><br/>

### Web Server

#### server/app/flask_app.py

<br/><br/>

### Data Ingest and Cleaning

#### server/app/csv_ingest.py

#### server/app/db.py

<br/><br/>

### Demo App Web Pages

<br/><br/>

### Topic Modeling



<br/><br/>

# 3) Usage <a name="usage"></a>

## Installation
This project is best setup with [Anaconda](https://www.anaconda.com/products/individual).
Virtualenv can be used but the installation instructions may not be applicable.

If using Anaconda, create your temporary environment:

```
conda create -n cs410_project_test python=3.7
conda activate cs410_project_test
```

If using virtualenv, do the equivalent.

Once your conda environment exists install the packages needed by the webserver & topic model.

```
cd src
chmod +x install.sh
Then either use pip (WARNING this may override your system Python if not in a virtualenv):
  ./install.sh
or anaconda to install required packages:
  /bin/bash install.sh -n  
```

A series of commands to run will be listed when installation is completed. Continue to the next section 
for instructions.


## How to Run

If on a unix system, set environment variables:

```
export FLASK_APP=app/flask_app.py
export FLASK_ENV=development
```

If on Windows, set the equivalent shell
[variable](https://stackoverflow.com/questions/51119495/how-to-setup-environment-variables-for-flask-run-on-windows).

Run the server: 


1. `cd server`
2. `flask routes`
3. `flask run --eager-loading`
4. Optional: if there is no .sqlite file in `src/server/instance`, you can create the database with: `flask init-db`. Don't do this if you are using the included db, as guided in these instructions as this can take quite some time.

Additional details on the server set up: 
* `flask routes` shows all the available urls. `flask init-db` doesn't run the webserver,
it creates the .sqlite database under the `src/server/instance/*` folder. This needs to be done before running
the webserver *unless* the checked-in database is available. The database setup may run for a few
minutes.
* `flask run --eager-loading` will run the webserver. The first time opening the URLS, the topic and
corpus data is uncached and the pages can take minutes to load. After the urls are opened successfully
at least once you should see .model and .corpus files in `src/instance/*`. The topic page may still
take a while to load but should be much faster.

Now the server is running and you can explore the model. In a browser, open any of the following URLs:
http://localhost:5000/index
http://127.0.0.1:5000/index
http://127.0.0.1:5000/topic/corpus
http://127.0.0.1:5000/topic/topic_main


### Retraining topic model
If you would like to retrain the model (and potentially see a different result due to LDA
being sensitive to initial conditions) you need to remove the existing model files. Once the
files are gone, reloading the topic URL will regenerate the topic model. This can take 5-10 minutes!
To reduce the runtime the constant `_DF_ROW_FRACTION=1.0` in `server/app/modelling.py` represents
the percent of documents to include in the topic mode. Setting `_DF_ROW_FRACTION=0.1` should reduce
the runtime by roughly 10x.

```
# Remove the existing model files.
> rm instance/lda_model.model*

# If you want to remove the corpus and BOW dictionary as well.
> rm instance/*.corpus

# If desired reduce the # of documents.
# The webserver should reload automatically due to the code change.
# If not reboot the Flask server.
> set _DF_ROW_FRACTION=0.1 in modelling.py

# Navigate to the topic url to generate and display the model. 
# Takes a long time!
> http://127.0.0.1:5000/topic/topic_main
```

Note: the ip may be different on your system, check the output of `flask run --eager-loading`
for the ip.


## Formatting
`yapf --in-place --recursive app/*.py *.py test/*.py`

<br/><br/>

## Uninstalling

To uninstall this web server:

```
conda remove --name cs410_project_test --all
conda info --envs
```
<br/><br/>

# 4) Contributors <a name="contributors"></a>

- Aaron Botelho (botelho3@) 100%
