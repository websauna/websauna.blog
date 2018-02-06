"""Functional tests."""

# SQLAlchemy
from sqlalchemy.orm.session import Session

from splinter.driver import DriverAPI


def test_empty_blog(web_server: str, browser: DriverAPI, dbsession: Session):
    """We can render empty blog."""

    # Direct Splinter browser to the website
    b = browser
    b.visit(web_server + "/blog/")

    # After login we see a profile link to our profile
    assert b.is_element_visible_by_css("#blog-no-posts")


def test_no_unpublished_in_blog_roll(web_server: str, browser: DriverAPI, dbsession: Session, unpublished_post_id):
    """Visitors should not see unpublished posts in blog roll."""

    # Direct Splinter browser to the website
    b = browser
    b.visit(web_server + "/blog/")

    # After login we see a profile link to our profile
    assert b.is_element_visible_by_css("#blog-no-posts")


def test_published_excerpt(web_server: str, browser: DriverAPI, dbsession: Session, published_post_id):
    """When posts are published they become visible in blog roll."""

    # Direct Splinter browser to the website
    b = browser
    b.visit(web_server + "/blog/")

    # After login we see a profile link to our profile
    assert b.is_element_visible_by_css(".excerpt")


def test_blog_pagination(web_server: str, browser: DriverAPI, dbsession: Session, publish_posts):
    """When posts exceed batch size, pagination is activated. Test that it's sane."""

    # Direct Splinter browser to the blog showing 5 items per page on page 1
    b = browser
    b.visit(web_server + "/blog/?batch_num=0&batch_size=5")

    # Iterate 5 times navigating with the 'Next' button
    for _ in range(5):
        # After the last 'Next' the button should be disabled
        if _ == 4:
            end_of_blog = b.find_by_xpath('//body/main/div[2]/div/div/div//ul/li[3]')
            # After 10 iterations the next button should be disabled
            assert end_of_blog.has_class("disabled")

        b.find_by_xpath('//body/main/div[2]/div/div/div//ul/li[3]/a').first.click()
