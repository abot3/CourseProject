# Schema
# CREATE TABLE corpus (
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   third_party_id INTEGER UNIQUE NOT NULL, #id from the kaggle database
#   document_name TEXT UNIQUE NOT NULL,
#   document_text TEXT NOT NULL
# );

# CREATE TABLE tags (
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   tag TEXT,
# );

# CREATE TABLE models (
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   third_party_id INTEGER UNIQUE NOT NULL, #id from the kaggle database
#   tags TEXT,
#   contributor_id INTEGER NOT NULL,
#   steps TEXT,
#   description TEXT,
#   ingredients TEXT,
#   n_ingredients INTEGER,
#   # model_type VARCHAR 
#   # author_id INTEGER NOT NULL,
#   # created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   # title TEXT NOT NULL,
#   # body TEXT NOT NULL,
#   # FOREIGN KEY (author_id) REFERENCES corpus (id)
#   FOREIGN KEY (doc_id) REFERENCES corpus (id)
# );

# INSERT INTO corpus() 
# VALUES ()

# RAW Recipes DF
# Index(['name', 'id', 'minutes', 'contributor_id', 'submitted', 'tags',
#        'nutrition', 'n_steps', 'steps', 'description', 'ingredients',
#        'n_ingredients'],
#       dtype='object')

#################################################################
# Insert Strings
#################################################################

_INSERT_RAW_RECIPES_CORPUS = '''
  INSERT INTO corpus (id, third_party_id, document_name, document_text)
  VALUES (NULL, ?, ?, ?)
'''

_INSERT_RAW_RECIPES_TAGS = '''
  INSERT INTO tags (id, tag)
  VALUES (NULL, ?)
'''

# _INSERT_RAW_RECIPES_MODELS = '''
#   INSERT INTO models (id, doc_id, third_party_id, tags, contributor_id, steps,
#     description, ingredients, n_ingredients)
#   VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)
# '''


_INSERT_RAW_RECIPES_MODELS = '''
  INSERT INTO models (id, doc_id, third_party_id, tags, contributor_id, steps,
    description, ingredients, n_ingredients)
  VALUES (NULL,
    (SELECT corpus.id FROM corpus WHERE corpus.third_party_id=?),
    ?, ?, ?, ?, ?, ?, ?)
'''


# Note sqlite has no concat operator
# JOIN tags ON models.tags LIKE CONCAT(\'%\', CONCAT(tags.tag, \'%\')) 
_INSERT_DOC_TAGS = '''
  INSERT INTO doc_tags (tag, tag_id, doc_id, third_party_id)
  WITH docs_by_tag AS (
    SELECT
      tags.tag,
      tags.id,
      models.doc_id,
      models.third_party_id
    FROM 
      models
    JOIN tags ON models.tags LIKE \'%\' || tags.tag || \'%\'
  )
  SELECT *
  FROM docs_by_tag
'''





#################################################################
# Query Strings
#################################################################

_SELECT_ALL_TEXT_DATA = '''
  SELECT 
    corpus.document_name,
    models.description,
    models.tags,
    models.steps,
    models.ingredients,
    models.third_party_id
  FROM corpus
  INNER JOIN models ON corpus.id=models.doc_id
'''

