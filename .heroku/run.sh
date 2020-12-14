#!/usr/bin/bash

echo "Creating db tables HTML"
python docs/database_tables.py

echo "Building docs"
make --directory=docs clean html

echo "Copying docs into static files dir"
cp -R docs/_build/html static/docs
