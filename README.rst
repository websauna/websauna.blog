This is a Python package for websauna.blog, an addon for `Websauna framework <https://websauna.org>`_.

Features
========

* One blog per site

* Markdown based editing

* RSS feed support

Installation
============

Local development mode
----------------------

Activate the virtual environment of your Websauna application.

Then::

    cd blog  # This is the folder with setup.py file
    pip install -e .

Running the development website
===============================

Local development machine
-------------------------

Example (OSX / Homebrew)::

    psql create blog_dev
    ws-sync-db websauna/blog/conf/development.ini
    ws-pserve websauna/blog/conf/development.ini --reload

Running the test suite
======================

First create test database::

    # Create database used for unit testing
    psql create blog_test

Install test and dev dependencies (run in the folder with ``setup.py``)::

    pip install -e ".[dev,test]"

Run test suite using py.test running::

    py.test

More information
================

Please see https://websauna.org/