"""Blog roll page functional tests."""

# Standard Library
import random

# Pyramid
import transaction

# SQLAlchemy
from sqlalchemy.orm.session import Session

import arrow
from splinter.driver import DriverAPI

# Websauna
from websauna.blog.tests.testing import pagination_test


def test_empty_blog(web_server: str, dbsession: Session, browser: DriverAPI):
    """We can render empty blog."""

    browser.visit(web_server + "/blog/")
    # After login we see a profile link to our profile
    assert browser.is_element_visible_by_css("#blog-no-posts")


def test_no_unpublished_posts_in_blog_roll(
    web_server: str, browser: DriverAPI, dbsession: Session, fakefactory
):
    """Visitors sees no unpublished posts in blog-roll."""

    # creating a private post, it should not be listed in roll for a visitor
    with transaction.manager:
        fakefactory.PostFactory(private=True)

    # after navigating to blog-roll there are no posts displayed
    browser.visit(web_server + "/blog/")
    assert browser.is_element_visible_by_css("#blog-no-posts")


def test_published_posts_in_blog_roll(web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
    """When posts are published they become visible in blog roll."""

    # creating a published post
    with transaction.manager:
        post = fakefactory.PostFactory(public=True)
        dbsession.expunge_all()

    # after navigating to blog-roll the post are displayed
    browser.visit(web_server + "/blog/")
    assert len(browser.find_by_css("div.post")) == 1
    post_line = browser.find_by_css("div.post")[0]
    assert post_line.find_by_css('h2').text == post.title
    assert post_line.find_by_css('.excerpt').text == post.excerpt
    assert (
        post_line.find_by_css('.text-muted').text ==
        'By {} just now. Tagged under {}.'.format(post.author, post.tags)
    )

    # user can navigate to post by clicking on its title on blog-roll page
    post_line.find_by_css('.post-link').click()
    assert browser.find_by_css("h1#heading-post").text == post.title


def test_posts_are_listed_in_publication_order(
    web_server: str, browser: DriverAPI, dbsession: Session, fakefactory
):
    """Post are listed in publication order on blog-roll."""

    dates_span = arrow.Arrow.range("hour", arrow.get(2013, 5, 5, 0, 0), arrow.get(2013, 5, 5, 19, 0))[::-1]
    with transaction.manager:
        posts = fakefactory.PostFactory.create_batch(len(dates_span), public=True)
        random.shuffle(posts)  # make sure that creation order is not the same as publication order
        for post, date in zip(posts, dates_span):
            post.published_at = date.datetime
        expected_posts_titles = [i.title for i in posts]

    browser.visit(web_server + "/blog/")
    rendered_posts_titles = [i.text for i in browser.find_by_css(".post h2")]

    assert expected_posts_titles == rendered_posts_titles


def test_blog_roll_pagination(web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
    """When posts exceed batch size, pagination is activated. Test that it's sane."""

    posts_per_page = 20
    with transaction.manager:
        posts = fakefactory.PostFactory.create_batch(100, public=True)[::-1]
        dbsession.expunge_all()

    browser.visit(web_server + "/blog/")
    pagination_test(browser, posts, posts_per_page, ".post h2")


def test_user_see_admin_panel_navigation(
        web_server: str, browser: DriverAPI, dbsession: Session, fakefactory, login_user):
    """Logged in user sees navigation link to admin panel on blog-roll."""

    with transaction.manager:
        user = fakefactory.UserFactory(admin=True)
        dbsession.expunge_all()
    login_user(user)
    browser.visit(web_server + "/blog/")

    # admin action menu is present
    assert browser.is_text_present("Admin actions")

    # after clicking on "Manage posts" user is redirected to posts-listing on admin panel
    browser.find_by_xpath('//a[text()[contains(.,"Manage posts")]]').click()
    assert browser.url.endswith('/admin/models/blog-posts/listing')


def test_visitor_does_not_see_admin_panel_navigation(
        web_server: str, browser: DriverAPI, dbsession: Session):
    """Admin actions are shown to logged in visitors only."""

    browser.visit(web_server + "/blog/")
    assert not browser.is_text_present("Admin actions")


def test_title_and_breadcrumbs(
        web_server: str, browser: DriverAPI, dbsession: Session):
    """Checking that breadcrumbs and post-roll title are displayed correctly."""

    blog_title = 'My little Websauna blog'

    browser.visit(web_server + "/blog/")
    assert browser.find_by_css('h1').text == blog_title
    assert browser.find_by_css('.breadcrumb').text.endswith(blog_title)
