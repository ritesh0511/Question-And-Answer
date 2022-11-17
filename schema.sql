DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS questions;

CREATE TABLE users (
                   id serial PRIMARY KEY,
                   name TEXT UNIQUE NOT NULL,
                   password TEXT NOT NULL,
                   admin INTEGER NOT NULL,
                   expert INTEGER NOT NULL
);

CREATE TABLE questions (
                        id serial PRIMARY KEY ,
                        question_text TEXT NOT NULL,
                        answer_text TEXT,
                        ask_by_id INTEGER NOT NULL,
                        expert_id INTEGER NOT NULL
);