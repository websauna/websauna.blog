"""Functional tests."""

from sqlalchemy.orm.session import Session
from splinter.driver import DriverAPI



def test_published_post(web_server: str, browser: DriverAPI, dbsession: Session, published_post_id):
    """User can view blog posts."""

    # Direct Splinter browser to the website
    b = browser
    b.visit(web_server + "/blog/")

    # After login we see a profile link to our profile
    assert b.find_by_css(".excerpt").click()

    assert b.is_element_not_present_by_css("#heading-post")