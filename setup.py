# Standard Library
import sys
from codecs import open
from os import path

from setuptools import find_packages
from setuptools import setup


assert sys.version_info >= (3, 5, 2), "Websauna needs Python 3.5.2 or newer, you have {version}".format(
    version=sys.version_info)

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    README = f.read()

with open(path.join(here, 'CHANGES.rst'), encoding='utf-8') as f:
    CHANGES = f.read()

# trying to run python setup.py install or python setup.py develop
if len(sys.argv) >= 2:
    if sys.argv[0] == "setup.py" and sys.argv[1] in ("install", "develop"):
        # Otherwise so much stuff would be broken later...
        raise RuntimeError(
            "It is not possible to install this package with setup.py. Use pip to install this package as instructed in Websauna tutorial.")

setup(
    name='websauna.blog',
    namespace_packages=['websauna'],
    version='1.0a3.dev0',
    description='Blog add on for Websauna',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
    ],
    url='https://websauna.org',
    author='Mikko Ohtamaa',
    author_email='mikko@opensourcehacker.com',
    license='MIT',
    keywords='web websauna pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='websauna.blog',
    install_requires=[
        'websauna',
        'rfeed',
        'docopt',
    ],
    extras_require={
        # Dependencies for running test suite
        'test': [
            'codecov',
            'flake8',
            'pytest>=3.0',
            'pytest-runner',
            'coverage',
            'flaky',
            'isort',
            'pytest-cov',
            'pytest-runner',
            'pytest-splinter',
            'pytest-timeout',
            'webtest',
            'factory_boy<=2.8.1',  # have dependency on internals...
            'pytest-cov',
        ],
        # Dependencies to make releases
        'dev': [
            'pyroma==2.2',  # This is needed until version 2.4 of Pyroma is released
            'sphinx>=1.6.1',
            'sphinx-autodoc-typehints',
            'sphinx_rtd_theme',
            'sphinxcontrib-zopeext',
            'sphinxcontrib-plantuml',
            'zest.releaser[recommended]',
        ],
    },

    # Define where this application starts as referred by WSGI web servers
    entry_points="""
        [paste.app_factory]
        main = websauna.blog.demo:main

        [console_scripts]
        ws-blog-createcontent = websauna.blog.scripts.createcontent:main
    """
)
