This is a Python package for websauna.blog, an addon for `Websauna framework <https://websauna.org>`_. You can use it as a simple blog for your site or as an example of Websaunsa design patterns.

.. contents:: :local:

Features
========

* Markdown based editing

* `Disqus <https://disqus.com>`_ based commenting

* Post description and meta for Google (SEO), Facebook, Twitter

* Drafts (admin only visible) and published posts

* RSS feed

* Basic unit and functional test suite

* One blog per site

Screenshots
===========

Blog post
---------

.. image:: https://github.com/websauna/websauna.blog/raw/master/screenshots/post.png

Admin
-----

.. image:: https://github.com/websauna/websauna.blog/raw/master/screenshots/admin.png

Installation
============

Adding to your site
-------------------

Include addon in your application initializer:

.. code-block:: python

    class Initializer(websauna.system.Initializer):

        def include_addons(self):
            """Include this addon in the configuration."""
            self.config.include("websauna.blog")


Example settings:

.. code-block:: ini

    # Title on blog roll
    blog.title = My little Websauna blog

    # this is "websauna" part from websaua.disqus.com/embed.js univeral
    # embed link
    blog.disqus_id = websauna

See ``nav.html`` example how to add a link to the blog in your site navigation.

Go to admin, start adding blog posts.

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