#!/usr/bin/bash

if [ 0 ]; then
  pip install flask
  pip install gensim
  pip install jinja
  pip install pytest coverage
  pip install numpy
  pip install pandas
  pip install tensorflow
  pip install torch
  pip install transformers
  pip install spacy 
  pip install ftfy
  pip install nltk 
else
  conda install flask
  conda install gensim
  conda install jinja
  conda install pytest coverage
  conda install numpy
  conda install pandas
  conda install tensorflow
  conda install torch
  conda install transformers
  conda install spacy 
  conda install ftfy
  conda install nltk
fi
export FLASK_APP=app/flask_app.py
export FLASK_ENV=development
