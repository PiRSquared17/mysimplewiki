-- Database creation script for the templated wiki engine
-- Copyright 2014 - Vitor Sonoki

DROP TABLE IF EXISTS main;

CREATE TABLE main (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    previous TEXT,
    changed TEXT
);
