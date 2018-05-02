"""Module level testing fixtures."""

# Thirdparty Library
import pytest


@pytest.fixture()
def fakefactory(dbsession):
    """Fixture for injecting db_session into fakefacktory module."""

    from websauna.blog.testing import fakefactory

    fakefactory.DB_SESSION_PROXY.session = dbsession
    try:
        yield fakefactory
    finally:
        fakefactory.DB_SESSION_PROXY.session = None
