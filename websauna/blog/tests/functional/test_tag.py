"""Functional tests."""

from sqlalchemy.orm.session import Session
from splinter.driver import DriverAPI


def test_empty_tag_roll(web_server: str, browser: DriverAPI, dbsession: Session):
    """We can render empty tag list."""

    # Direct Splinter browser to the website
    b = browser
    b.visit(web_server + "/blog/tag/xxx")

    # After login we see a profile link to our profile
    assert b.is_element_present_by_css("#blog-no-posts")


def test_tag_roll(web_server: str, browser: DriverAPI, dbsession: Session, published_post_id):
    """We render tagged posts in their tag roll."""

    # Direct Splinter browser to the website
    b = browser
    b.visit(web_server + "/blog/tag/mytag")

    # After login we see a profile link to our profile
    import pdb ; pdb.set_trace()
    assert b.is_element_present_by_css(".excerpt")