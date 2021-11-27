DROP TABLE IF EXISTS corpus;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS doc_tags;
DROP TABLE IF EXISTS models;

PRAGMA foreign_keys = ON;

CREATE TABLE corpus (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  third_party_id INTEGER UNIQUE NOT NULL, --id from the kaggle database
  document_name TEXT UNIQUE NOT NULL,
  document_text TEXT NOT NULL
);

CREATE TABLE tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tag TEXT
);

CREATE TABLE doc_tags (
  tag TEXT,
  tag_id INTEGER NOT NULL,
  doc_id INTEGER NOT NULL,
  third_party_id INTEGER NOT NULL,
  FOREIGN KEY (tag_id) REFERENCES tags (id),
  FOREIGN KEY (doc_id) REFERENCES corpus (id)
);

CREATE TABLE models (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doc_id INTEGER UNIQUE NOT NULL, -- id from corpus table
  third_party_id INTEGER UNIQUE NOT NULL, --id from the kaggle database
  tags TEXT,
  contributor_id INTEGER NOT NULL,
  steps TEXT,
  description TEXT,
  ingredients TEXT,
  n_ingredients INTEGER
  -- n_ingredients INTEGER,
  -- model_type VARCHAR 
  -- author_id INTEGER NOT NULL,
  -- created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  -- title TEXT NOT NULL,
  -- body TEXT NOT NULL,
  -- FOREIGN KEY (author_id) REFERENCES corpus (id)
  -- FOREIGN KEY (doc_id) REFERENCES corpus (id)
);
