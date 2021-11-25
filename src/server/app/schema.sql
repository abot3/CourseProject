DROP TABLE IF EXISTS corpus;
DROP TABLE IF EXISTS doc_tags;
DROP TABLE IF EXISTS models;

CREATE TABLE corpus (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  third_party_id INTEGER UNIQUE NOT NULL, --id from the kaggle database
  tag_id INTEGER UNIQUE NOT NULL,  --
  document_name TEXT UNIQUE NOT NULL,
  document_text TEXT NOT NULL
);

CREATE TABLE doc_tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tag TEXT,
  FOREIGN KEY (id) REFERENCES corpus (id)
);

CREATE TABLE models (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  model_type VARCHAR 
  -- author_id INTEGER NOT NULL,
  -- created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  -- title TEXT NOT NULL,
  -- body TEXT NOT NULL,
  -- FOREIGN KEY (author_id) REFERENCES corpus (id)
);
