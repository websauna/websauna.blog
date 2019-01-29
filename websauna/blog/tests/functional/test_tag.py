"""Functional tests."""
# Standard Library
import random
from uuid import uuid4

# Pyramid
import transaction

# SQLAlchemy
from sqlalchemy.orm.session import Session

# Thirdparty Library
import arrow
from splinter.driver import DriverAPI

# Websauna
from websauna.blog.tests.testing import pagination_test


def test_empty_tag_roll(web_server: str, browser: DriverAPI, dbsession: Session):
    """We can render empty tag list."""

    # Direct Splinter browser to the website
    browser.visit(web_server + "/blog/tag/xxx")

    assert browser.is_element_present_by_css("#blog-no-posts")


def test_visitor_sees_only_relevant_posts_in_tag_roll(
    web_server: str, browser: DriverAPI, dbsession: Session, fakefactory
):
    """Visitors should not see unpublished posts in blog roll."""

    with transaction.manager:
        tag = uuid4().hex
        post = fakefactory.PostFactory(public=True, tags=tag)
        fakefactory.PostFactory()
        dbsession.expunge_all()

    browser.visit(web_server + "/blog/tag/{}".format(tag))
    assert len(browser.find_by_css("div.post")) == 1
    assert browser.is_text_present(post.title)


def test_visitor_sees_only_published_posts_in_tag_roll(
    web_server: str, browser: DriverAPI, dbsession: Session, fakefactory
):
    """Visitors should not see unpublished posts in blog roll."""

    with transaction.manager:
        tag = uuid4().hex
        fakefactory.PostFactory(private=True, tags=tag)
        dbsession.expunge_all()

    browser.visit(web_server + "/blog/tag/{}".format(tag.title))
    assert browser.is_element_visible_by_css("#blog-no-posts")


def test_tag_roll_pagination(web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
    """When posts exceed batch size, pagination is activated. Test that it's sane."""
    posts_per_page = 20
    with transaction.manager:
        tag = uuid4().hex
        posts = fakefactory.PostFactory.create_batch(100, public=True, tags=tag)
        dbsession.expunge_all()

    browser.visit(web_server + "/blog/tag/{}".format(tag))
    pagination_test(browser, posts, posts_per_page, ".post h2")


def test_posts_are_listed_in_publication_order(
    web_server: str, browser: DriverAPI, dbsession: Session, fakefactory
):
    """Post are listed in publication order on blog-roll."""

    dates_span = arrow.Arrow.range("hour", arrow.get(2013, 5, 5, 0, 0), arrow.get(2013, 5, 5, 19, 0))[::-1]
    with transaction.manager:
        tag = uuid4().hex
        posts = fakefactory.PostFactory.create_batch(len(dates_span), public=True, tags=tag)
        random.shuffle(posts)  # make sure that creation order is not the same as publication order
        for post, date in zip(posts, dates_span):
            post.published_at = date.datetime
        expected_posts_titles = [i.title for i in posts]

    browser.visit(web_server + "/blog/tag/{}".format(tag))

    rendered_posts_titles = [i.text for i in browser.find_by_css(".post h2")]

    assert expected_posts_titles == rendered_posts_titles


def test_title_and_breadcrumbs(
        web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
    """Checking that breadcrumbs and post-roll title are displayed correctly."""

    with transaction.manager:
        tag = uuid4().hex
        fakefactory.PostFactory(public=True, tags=tag)
        dbsession.expunge_all()

    blog_title = 'Posts tagged {}'.format(tag)
    browser.visit(web_server + "/blog/tag/{}".format(tag))

    assert browser.find_by_css('h1').text == blog_title
    assert browser.find_by_css('.breadcrumb').text.endswith(blog_title)
