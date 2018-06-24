"""Functional tests."""
# Thirdparty Library
import transaction
from splinter.driver import DriverAPI
from sqlalchemy.orm.session import Session

# Websauna's Blog Addon
from websauna.blog.testing.helpers import login_user


def loggedin_user_is_on_posts_list(browser, fakefactory, dbsession, web_server, params=None):
    with transaction.manager:
        user = fakefactory.AdminFactory()
        post = fakefactory.PostFactory(author=user, **(params or {}))
        dbsession.expunge_all()

    login_user(web_server, browser, user)
    browser.visit(web_server + "/blog/")
    browser.find_by_css("a#nav-admin").click()
    browser.find_by_css("a#btn-panel-list-blog-posts").click()

    return user, post


def test_add_post(web_server: str, dbsession: Session, browser: DriverAPI, fakefactory):
    user, _ = loggedin_user_is_on_posts_list(browser, fakefactory, dbsession, web_server)
    browser.find_by_css("a#btn-crud-add").click()
    post = fakefactory.PostFactory.build(state="private", body="HELLO")

    browser.type("title", post.title)
    browser.type("excerpt", post.excerpt)

    # small hack to make provide and id for `get_iframe` function
    iframe_id = "qwerty"
    browser.execute_script("$('iframe').attr('id', '%s');" % iframe_id)

    # TODO: add tag creation test

    with browser.get_iframe(iframe_id) as iframe:
        iframe.find_by_tag("body").type(post.body)

    browser.find_by_css("button#deformadd").click()

    assert browser.find_by_css("h1").text == post.title

    rendered_fields = {
        i.find_by_css(".control-label").text: getattr(i.find_by_css(".form-control-static"), "text", None)
        for i in browser.find_by_css("div.form-group")
    }

    assert bool(rendered_fields["Created At"])
    assert rendered_fields["Author"] == str(user)
    assert rendered_fields["Excerpt"] == post.excerpt
    assert not bool(rendered_fields["Published At"])
    assert bool(rendered_fields["Slug"])
    assert rendered_fields["State"] == "private"
    assert rendered_fields["Tags"] is None
    assert rendered_fields["Title"] == post.title
    assert not bool(rendered_fields["Updated At"])
    assert rendered_fields["Body"].replace("<p>", "").replace("</p>", "").replace(" ", "").replace("\n", "").replace(
        "&nbsp;", ""
    ) == post.body.replace(" ", "").replace("\n", "")


def test_edit_post(web_server: str, dbsession: Session, browser: DriverAPI, fakefactory):
    user, post = loggedin_user_is_on_posts_list(browser, fakefactory, dbsession, web_server, params=dict(body="HELLO"))
    new_post_data = fakefactory.PostFactory.build(body="qwery")
    browser.find_by_css("a.btn-crud-listing-edit").click()

    browser.type("title", new_post_data.title)
    browser.type("excerpt", new_post_data.excerpt)

    # small hack to make provide and id for `get_iframe` function
    iframe_id = "qwerty"
    browser.execute_script("$('iframe').attr('id', '%s');" % iframe_id)

    # TODO: add tag editing test

    with browser.get_iframe(iframe_id) as iframe:
        iframe.find_by_tag("body").type(new_post_data.body)

    browser.find_by_css("button#deformsave").click()
    assert browser.find_by_css("h1").text == post.title + new_post_data.title

    rendered_fields = {
        i.find_by_css(".control-label").text: getattr(i.find_by_css(".form-control-static"), "text", None)
        for i in browser.find_by_css("div.form-group")
    }

    assert bool(rendered_fields["Created At"])
    assert rendered_fields["Author"] == str(post.author)
    assert rendered_fields["Excerpt"] == post.excerpt + new_post_data.excerpt
    assert bool(rendered_fields["Published At"])
    assert rendered_fields["Slug"] == post.slug
    assert rendered_fields["State"] == "public"
    assert rendered_fields["Tags"] is not None
    assert rendered_fields["Title"] == post.title + new_post_data.title
    assert bool(rendered_fields["Updated At"])
    assert rendered_fields["Body"].replace("<p>", "").replace("</p>", "").replace("\n", "").replace(" ", "") == (
        new_post_data.body + post.body
    ).replace("\n", "").replace(" ", "")


def test_delete_post(web_server: str, dbsession: Session, browser: DriverAPI, fakefactory):
    user, post = loggedin_user_is_on_posts_list(browser, fakefactory, dbsession, web_server)
    browser.find_by_css("a.btn-crud-listing-delete").click()
    assert browser.is_text_present(post.title)
    assert browser.is_text_present("Confirm delete")
    browser.find_by_css("#btn-delete-yes").click()
    assert browser.is_text_present("No items")


def test_list_posts(web_server: str, dbsession: Session, browser: DriverAPI, fakefactory):
    user, post = loggedin_user_is_on_posts_list(browser, fakefactory, dbsession, web_server)
    post_line = browser.find_by_css(".crud-row-{}".format(post.id))
    assert post_line.find_by_css(".crud-column-title").text == post.title
    assert post_line.find_by_css(".crud-column-state").text == post.state
    assert post_line.find_by_css(".crud-column-created_at").text == "just now"
    assert post_line.find_by_css(".crud-column-published_at").text == "just now"
    assert post_line.find_by_css(".crud-column-author").text == str(post.author)

    # title link navigation test
    post_line.find_by_css(".crud-column-title a").click()
    assert browser.find_by_css("h1").text == (post.title)


def test_publish_post(web_server: str, dbsession: Session, browser: DriverAPI, fakefactory):
    user, post = loggedin_user_is_on_posts_list(
        browser, fakefactory, dbsession, web_server, params={"state": "private"}
    )
    browser.find_by_css("a.btn-crud-listing-show").click()
    browser.find_by_css("#btn-crud-btn-publish-post").click()
    assert browser.is_text_present("The post has been published.")
    assert browser.find_by_css("#btn-crud-btn-retract-post")


def test_retract_post(web_server: str, dbsession: Session, browser: DriverAPI, fakefactory):
    user, post = loggedin_user_is_on_posts_list(browser, fakefactory, dbsession, web_server)
    browser.find_by_css("a.btn-crud-listing-show").click()
    browser.find_by_css("#btn-crud-btn-retract-post").click()
    assert browser.is_text_present("The post has been retracted.")
    assert browser.find_by_css("#btn-crud-btn-publish-post")


def test_view_on_site(web_server: str, dbsession: Session, browser: DriverAPI, fakefactory):
    user, post = loggedin_user_is_on_posts_list(browser, fakefactory, dbsession, web_server)

    browser.find_by_css("a.btn-crud-listing-show").click()

    browser.find_by_css("#btn-crud-btn-view-on-site").click()

    assert browser.find_by_css("#heading-post").text == post.title
