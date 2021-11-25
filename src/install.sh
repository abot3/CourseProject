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
  pip install spacy 
  pip install ftfy
fi
export FLASK_APP=app/flask_app.py
export FLASK_ENV=development
