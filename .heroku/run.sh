#!/usr/bin/bash

echo "Creating db tables HTML"
pipenv run db_tables

echo "Building docs"
pipenv run docs

echo "Copying docs into static files dir"
pipenv run docs_static
