#!/usr/bin/bash

# conda create -n cs410_topic_model python=3.7
# conda activate cs410_topic_model

# Set variables
use_conda=0
Red=$'\e[1;31m'
Green=$'\e[1;32m'
Blue=$'\e[1;34m'

Help()
{
   # Display Help
   echo "Install the Python modules for the server in the current directory."
   echo
   echo "Syntax: scriptTemplate [-n|h]"
   echo "options:"
   echo "n     Use anaconda instead of pip."
   echo "h     Print this Help."
   echo
}

# Get the options
while getopts ":hn:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      n) # Enter a name
         use_conda=1;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

if [ $use_conda -eq 0 ]; then
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
  pip install spacy
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
  conda install spacy
fi
echo "$Green Installation complete!"
echo "$Red Please run the following commands:"
echo "$Green export FLASK_APP=app/flask_app.py"
echo "$Green export FLASK_ENV=development"
echo "$Green cd server"
echo "$Green flask routes"
echo "$Green flask run --eager-loading"
echo "$Green flask init-db  --don't do this if you are using the included db."
