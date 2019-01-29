"""``websauna.blog`` top level fixtures."""
import pytest


@pytest.fixture()
def fakefactory(dbsession):
    """Fakefactory fixture for creating dummy content.

    Fixture attaches sqlachemy session to ``factory_boy`` content factories
    via ``DBSessionProxy`` and provides module with factories as a dependency
    injection for tests.

    note::

        Using `recommended recipe on attaching session to factories`_
        with usage of ``scoped_session`` will result in having different
        sessions for tests and factories, that is why session is shared
        to factories via proxy, which is set up by this fixture.


    warning:: the fixture is not thread safe

    .. _recommended recipe on attaching session to factories: https://factoryboy.readthedocs.io/en/latest/orms.html#managing-sessions

    """

    from websauna.blog.tests import fakefactory
    fakefactory.DB_SESSION.session = dbsession
    try:
        yield fakefactory
    finally:
        fakefactory.DB_SESSION.session = None


@pytest.fixture()
def login_user(web_server, browser):
    """Fixture that return function to log user in"""

    def login_user(user):
        browser.visit(web_server + "/login")
        browser.fill("username", user.email)
        browser.fill("password", "qwerty")  # XXX: hardcoded password
        browser.find_by_name("login_email").click()
        assert browser.is_element_present_by_css("#nav-logout")

    yield login_user
