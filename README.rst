This is a Python package for websauna.blog, an addon for `Websauna framework <https://websauna.org>`_. You can use it as a simple blog for your site or as an example of Websaunsa design patterns.

.. |ci| image:: https://img.shields.io/travis/websauna/websauna.blog/master.svg?style=flat-square
    :target: https://travis-ci.org/websauna/websauna.blog/

.. |cov| image:: https://codecov.io/github/websauna/websauna.blog/coverage.svg?branch=master
    :target: https://codecov.io/github/websauna/websauna.blog?branch=master

.. |latest| image:: https://img.shields.io/pypi/v/websauna.blog.svg
    :target: https://pypi.python.org/pypi/websauna.blog/
    :alt: Latest Version

.. |license| image:: https://img.shields.io/pypi/l/websauna.blog.svg
    :target: https://pypi.python.org/pypi/websauna.blog/
    :alt: License

.. |versions| image:: https://img.shields.io/pypi/pyversions/websauna.blog.svg
    :target: https://pypi.python.org/pypi/websauna.blog/
    :alt: Supported Python versions

+-----------+-----------+-----------+
| |versions|| |latest|  | |license| |
+-----------+-----------+-----------+
| |ci|      | |cov|     |           |
+-----------+-----------+-----------+

.. contents:: :local:

Features
========

* Markdown based editing

* `Disqus <https://disqus.com>`_ based commenting

* Post description and meta for Google (SEO), Facebook, Twitter. Sitemap support and Google Article metadata support.

* Blog post management through Websauna admin interface

* Drafts (admin only visible) and published posts

* RSS feed

* Basic unit and functional test suite

Note that this addon is not intended to be used as is, but more of an example. You most likely want to fork it over and modify for your own needs.

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

    # The email appearing in RSS feed
    # (It is recommended not to use any real email)
    blog.rss_feed_email = no-reply@example.com

See ``nav.html`` example how to add a link to the blog in your site navigation.

Add RSS feed discovery by customizing ``site/meta.html`` template:

.. code-block:: html

    {# Misc ``<meta>`` tags in ``<head>``. #}

    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta name="viewport" content="width=device-width" />

    {% include "blog/rss_head.html" %}

Create migrations for blog post SQL table for your site::

    ws-alembic -c myapp/conf/development.ini -x packages=all revision --auto -m "Adding blog content types"

Run migrations::

     ws-alembic -c myapp/conf/development.ini -x packages=all upgrade head

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
    ws-create-user websauna/blog/conf/development.ini admin@example.com mypassword
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