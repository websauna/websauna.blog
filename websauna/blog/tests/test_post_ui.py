"""Functional tests."""
# Thirdparty Library
# Pyramid
import transaction
from splinter.driver import DriverAPI
# SQLAlchemy
from sqlalchemy.orm.session import Session

# Websauna's Blog Addon
from websauna.blog.testing.helpers import login_user


def test_visitor_published_post(web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
    """User can view blog posts."""

    with transaction.manager:
        post = fakefactory.PostFactory()
        dbsession.expunge_all()

    browser.visit(web_server + "/blog/")

    assert browser.is_element_present_by_css("#heading-blog")

    browser.find_by_xpath('//a[text()[contains(.,"{}")]]'.format(post.title)).click()

    # checking title
    assert browser.find_by_css("h1#heading-post").text == post.title

    # checking tags
    rendered_post_tags = [i.text for i in browser.find_by_css(".tags-line a")]
    post_tags = [i.title for i in post.tags]
    assert len(rendered_post_tags) == len(post_tags)
    assert set(rendered_post_tags) == set(post_tags)

    # checking body
    assert browser.find_by_css("div#post-body-text").text == post.body.replace("\n", " ")


def test_private_post(web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
    with transaction.manager:
        user = fakefactory.AdminFactory()
        post = fakefactory.PostFactory(state="private")
        dbsession.expunge_all()
    login_user(web_server, browser, user)
    browser.visit(web_server + "/blog/" + post.slug)
    # private higlight
    assert browser.find_by_id("heading-post").has_class("text-danger")


def test_admin_panel_navigation(web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
    with transaction.manager:
        user = fakefactory.AdminFactory()
        post = fakefactory.PostFactory()
        dbsession.expunge_all()
    login_user(web_server, browser, user)
    browser.visit(web_server + "/blog/" + post.slug)


def test_breadcrumbs(web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
    """When posts are published they become visible in blog roll."""
    with transaction.manager:
        post = fakefactory.PostFactory()
        dbsession.expunge_all()
    browser.visit(web_server + "/blog/" + post.slug)
    assert browser.find_by_css(".breadcrumb").text == "Home My little Websauna blog " + post.title


def test_unahtorize_accesse(web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
    """When posts are published they become visible in blog roll."""
    with transaction.manager:
        post = fakefactory.PostFactory(state="private")
        dbsession.expunge_all()
    browser.visit(web_server + "/blog/" + post.slug)
    # private higlight
    assert browser.find_by_css("h1").text == "Forbidden"
