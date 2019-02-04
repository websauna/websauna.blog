"""Functional tests."""
import transaction

# SQLAlchemy
from sqlalchemy.orm.session import Session

from splinter.driver import DriverAPI


def test_published_post(web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
    """User can view blog posts."""
    with transaction.manager:
        fakefactory.PostFactory(public=True)

    b = browser
    b.visit(web_server + "/blog/")

    assert b.is_element_present_by_css("#heading-blog")

    # Go to the published post from the roll
    b.find_by_css(".post-link").click()

    assert b.is_element_present_by_css("#heading-post")
