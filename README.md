# CourseProject

Please fork this repository and paste the github link of your fork on Microsoft CMT. Detailed instructions are on Coursera under Week 1: Course Project Overview/Week 9 Activities.

# Overview

# Installation
```
c
cd src
chmod +x install.sh
Then either:
  ./install.sh -n
or if in anaconda env:
  /bin/bash install.sh -n  
```

# Run
```
export FLASK_APP=app/flask_app.py
export FLASK\_ENV=development
cd server
flask routes
flask run --eager-loading  
flask init-db  --don't do this if you are using the included db.
```

# Project Layout

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


# Formatting
`yapf --in-place --recursive app/*.py *.py test/*.py`

<br/><br/>

# Overview of Code
### 1) An overview of the function of the code (i.e., what it does and what it can be used for).

As stated in the project proposal the purpose of this code is to provide an implementation
of text clustering/topic modeling for a commonly used web server. With the popularity of 
user generated content on todays websites it's important for smaller sites to be able to
interpret and discover topics or clusters within their text data. 

An example app was developed using the Flask webserver.
Flask was chosen for its popularity, simplicity, and due to it being written in Python.
This project also makes use of Pandas, Numpy,
and Gensim libraries for building the data cleaning, and building the topic model. All these libraries are
written in Python, so installation and integration with the server is straightforward.

The example app contains data cleaning, topic modeling, and storage functions that can be
re-used by any Flask app. However, much of the code is currently tied to the specific dataset used
by the example app, a corpus of cooking recipes from `food.com`. Future work could focus on
decoupling the strings and keywords specific to the `food.com` dataset from the generic 
topic modeling and storage functions. The generic code can be factored out into a
Flask plugin. Currently the demo app act as a proof of concept rather than a fully independent
plugin.

The proof-of-concept app ingests a corpus of [cooking recipe data](https://www.kaggle.com/shuyangli94/food-com-recipes-and-user-interactions?select=RAW_recipes.csv) retrieved from Kaggle. The raw data contains
~230,000 unique recipes with the text fields `name, description, steps(preparation), tags(categories), and description`.
The data is in `.csv` format and is cleaned, deduplicated, tokenized, stemmed using Panda and Gensim 
(see `csv_ingest.py`, `db.py`). The cleaned dataset is then inserted in to a SQL (sqlite) database,
allowing simple analysis and easy keyword filtering (see `sql_strings.py`, `schema.sql`). Post filtering
a SQL query is run, retrieving ~120k rows from the database. The 120k rows are fed to the topic model
and the results are rendered in the web app. The corpus and bag-of-words representation of the 

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

<br/><br/>

# 2) Architecture & Key Functions
### 2) Documentation of how the software is implemented with sufficient detail so that others can have a basic understanding of your code for future extension or any further improvement.

### Data Ingest and Cleaning

<br/><br/>

### Demo App Web Pages

<br/><br/>

### Topic Modeling



<br/><br/>

## 3) How to Run the Code
### 3) Documentation of the usage of the software including either documentation of usages of APIs or detailed instructions on how to install and run a software, whichever is applicable.

<br/><br/>

# 4) Contributors

- Aaron Botelho (botelho3@) 100%
