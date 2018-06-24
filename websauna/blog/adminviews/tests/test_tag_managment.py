"""Functional tests."""
# Thirdparty Library
import transaction
from splinter.driver import DriverAPI
from sqlalchemy.orm.session import Session

# Websauna's Blog Addon
from websauna.blog.testing.helpers import login_user


def loggedin_user_is_on_tags_list(browser, fakefactory, dbsession, web_server, params=None):
    with transaction.manager:
        user = fakefactory.AdminFactory()
        tag = fakefactory.TagFactory(**(params or {}))
        dbsession.expunge_all()

    login_user(web_server, browser, user)
    browser.visit(web_server + "/blog/")
    browser.find_by_css("a#nav-admin").click()
    browser.find_by_css("a#btn-panel-list-blog-tags").click()

    return user, tag


def test_add_tag(web_server: str, dbsession: Session, browser: DriverAPI, fakefactory):
    user, _ = loggedin_user_is_on_tags_list(browser, fakefactory, dbsession, web_server)

    browser.find_by_css("a#btn-crud-add").click()
    tag = fakefactory.TagFactory.build()
    browser.type("title", tag.title)
    browser.find_by_css("button#deformadd").click()

    assert browser.find_by_css("h1").text == tag.title


def test_edit_tag(web_server: str, dbsession: Session, browser: DriverAPI, fakefactory):
    user, tag = loggedin_user_is_on_tags_list(browser, fakefactory, dbsession, web_server)

    new_tag_data = fakefactory.TagFactory.build()
    browser.find_by_css("a.btn-crud-listing-edit").click()
    browser.type("title", new_tag_data.title)
    browser.find_by_css("button#deformsave").click()

    assert browser.find_by_css("h1").text == tag.title + new_tag_data.title


def test_delete_tag(web_server: str, dbsession: Session, browser: DriverAPI, fakefactory):
    user, tag = loggedin_user_is_on_tags_list(browser, fakefactory, dbsession, web_server)
    browser.find_by_css("a.btn-crud-listing-delete").click()
    assert browser.is_text_present(tag.title)
    assert browser.is_text_present("Confirm delete")
    browser.find_by_css("#btn-delete-yes").click()
    assert browser.is_text_present("No items")


def test_list_tags(web_server: str, dbsession: Session, browser: DriverAPI, fakefactory):
    user, tag = loggedin_user_is_on_tags_list(browser, fakefactory, dbsession, web_server)
    tag_line = browser.find_by_css(".crud-row-{}".format(tag.id))
    assert tag_line.find_by_css(".crud-column-title").text == tag.title

    # title link navigation test
    tag_line.find_by_css(".crud-column-title a").click()
    assert browser.find_by_css("h1").text == ("Posts tagged " + tag.title)
