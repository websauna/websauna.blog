# Standard Library
import random

# Thirdparty Library
import arrow
import transaction
from splinter.driver import DriverAPI
from sqlalchemy.orm.session import Session

# Websauna's Blog Addon
from websauna.blog.testing.helpers import login_user


def test_empty_blog(web_server: str, dbsession: Session, browser: DriverAPI):
    """We can render empty blog."""

    browser.visit(web_server + "/blog/")
    # After login we see a profile link to our profile
    assert browser.is_element_visible_by_css("#blog-no-posts")


def test_visitor_sees_no_unpublished_posts_in_blog_roll(
    web_server: str, browser: DriverAPI, dbsession: Session, fakefactory
):
    """Visitors should not see unpublished posts in blog roll."""

    with transaction.manager:
        fakefactory.PostFactory(state="private")

    browser.visit(web_server + "/blog/")

    # After login we see a profile link to our profile
    assert browser.is_element_visible_by_css("#blog-no-posts")


def test_visitor_sees_published_posts_in_blog_roll(
    web_server: str, browser: DriverAPI, dbsession: Session, fakefactory
):
    """When posts are published they become visible in blog roll."""

    with transaction.manager:
        post = fakefactory.PostFactory()
        fakefactory.PostFactory(state="private")
        dbsession.expunge_all()

    browser.visit(web_server + "/blog/")

    # only one post should be listed
    assert len(browser.find_by_css("div.post")) == 1

    # After login we see a profile link to our profile
    assert browser.is_text_present(post.title)
    assert browser.is_text_present(post.excerpt)


def test_published_posts_are_listed_in_publication_order(
    web_server: str, browser: DriverAPI, dbsession: Session, fakefactory
):
    """When posts are published they become visible in blog roll."""

    dates_span = arrow.Arrow.range("hour", arrow.get(2013, 5, 5, 0, 0), arrow.get(2013, 5, 5, 20, 0))[::-1]
    with transaction.manager:
        posts = fakefactory.PostFactory.create_batch(20)
        random.shuffle(posts)
        for post, date in zip(posts, dates_span):
            post.published_at = date.datetime
        expected_posts_titles = [i.title for i in posts]

    browser.visit(web_server + "/blog/")
    rendered_posts_titles = [i.text for i in browser.find_by_css(".post h2")]

    assert expected_posts_titles == rendered_posts_titles


def test_unpublished_posts_are_listed_in_creation_order(
    web_server: str, browser: DriverAPI, dbsession: Session, fakefactory
):
    """When posts are published they become visible in blog roll."""

    with transaction.manager:
        user = fakefactory.AdminFactory()
        dbsession.expunge_all()
    login_user(web_server, browser, user)

    dates_span = arrow.Arrow.range("hour", arrow.get(2013, 5, 5, 0, 0), arrow.get(2013, 5, 5, 20, 0))[::-1]
    with transaction.manager:
        posts = fakefactory.PostFactory.create_batch(20, state="private", published_at=None)
        random.shuffle(posts)
        for post, date in zip(posts, dates_span):
            post.created_at = date.datetime
        expected_posts_titles = [i.title for i in posts]

    browser.visit(web_server + "/blog/")
    rendered_posts_titles = [i.text for i in browser.find_by_css(".post h2")]

    assert expected_posts_titles == rendered_posts_titles


def test_unpublished_posts_are_listed_before_published(
    web_server: str, browser: DriverAPI, dbsession: Session, fakefactory
):
    """When posts are published they become visible in blog roll."""

    with transaction.manager:
        user = fakefactory.AdminFactory()
        dbsession.expunge_all()
    login_user(web_server, browser, user)

    dates_span = arrow.Arrow.range("hour", arrow.get(2013, 5, 5, 0, 0), arrow.get(2013, 5, 5, 20, 0))[::-1]
    with transaction.manager:
        published_posts = fakefactory.PostFactory.create_batch(10)
        unpublished_posts = fakefactory.PostFactory.create_batch(10, state="private", published_at=None)
        posts = unpublished_posts + published_posts
        random.shuffle(posts)
        for post, date in zip(posts, dates_span):
            attr = "created_at" if post.state == "private" else "published_at"
            setattr(post, attr, date.datetime)
        expected_posts_titles = [i.title for i in unpublished_posts + published_posts]

    browser.visit(web_server + "/blog/")
    rendered_posts_titles = [i.text for i in browser.find_by_css(".post h2")]

    assert set(expected_posts_titles[:10]) == set(rendered_posts_titles[:10])
    assert set(expected_posts_titles[10:]) == set(rendered_posts_titles[10:])


def test_authors_sees_unpublished_they_own_posts_on_blog_roll(
    web_server: str, browser: DriverAPI, dbsession: Session, fakefactory
):

    with transaction.manager:
        user = fakefactory.UserFactory()
        published_post = fakefactory.PostFactory(author=user)
        unpublished_post = fakefactory.PostFactory(author=user, state="private")
        fakefactory.PostFactory(state="private")
        dbsession.expunge_all()

    login_user(web_server, browser, user)

    browser.visit(web_server + "/blog/")

    # only one post should be listed
    assert len(browser.find_by_css("div.post")) == 2
    assert browser.is_text_present(published_post.title)
    assert browser.is_text_present(unpublished_post.title)


def test_managers_sees_unpublished_posts_on_blog_roll(
    web_server: str, browser: DriverAPI, dbsession: Session, fakefactory
):
    with transaction.manager:
        user = fakefactory.AdminFactory()
        published_post = fakefactory.PostFactory()
        unpublished_post = fakefactory.PostFactory(state="private")
        dbsession.expunge_all()

    login_user(web_server, browser, user)

    browser.visit(web_server + "/blog/")

    # only one post should be listed
    assert len(browser.find_by_css("div.post")) == 2
    assert browser.is_text_present(published_post.title)
    assert browser.is_text_present(unpublished_post.title)


def test_blog_roll_pagination(web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
    """When posts exceed batch size, pagination is activated. Test that it's sane."""
    posts_per_page = 20
    with transaction.manager:
        posts = fakefactory.PostFactory.create_batch(100)[::-1]
        dbsession.expunge_all()

    browser.visit(web_server + "/blog/")

    def pagination_element(text, disabled=False):
        return browser.find_by_xpath(
            '//div[@class="pagination-wrapper"]//li[@class="{disabled}"]/a[text()[contains(.,"{text}")]]'.format(
                text=text, disabled="disabled" if disabled else ""
            )
        )

    # checking disabled buttons (First and Previous)
    assert pagination_element("First", disabled=True)
    assert pagination_element("Previous", disabled=True)

    # checking not disabled buttons (Next and Last)
    assert pagination_element("Next")
    assert pagination_element("Last")

    # navigating to the last page (checking that Last works correctly)
    pagination_element("Last").click()
    rendered_posts_titles = [i.text for i in browser.find_by_css(".post h2")]
    assert rendered_posts_titles == [i.title for i in posts[-posts_per_page:]]

    # checking not disabled buttons (First and Previous)
    assert pagination_element("First")
    assert pagination_element("Previous")

    # checking disabled buttons (Next and Last)
    assert pagination_element("Next", disabled=True)
    assert pagination_element("Last", disabled=True)

    # navigating to the first page (checking that First works correctly)
    pagination_element("First").click()
    rendered_posts_titles = [i.text for i in browser.find_by_css(".post h2")]
    assert rendered_posts_titles == [i.title for i in posts[:posts_per_page]]

    # checking if "next" works correctly
    for page in range(0, len(posts), posts_per_page):
        rendered_posts_titles = [i.text for i in browser.find_by_css(".post h2")]
        assert rendered_posts_titles == [i.title for i in posts[page : page + posts_per_page]]
        if page < len(posts) - posts_per_page:
            pagination_element("Next").click()

    # checking if "prev" works correctly
    for page in range(0, len(posts), posts_per_page):
        rendered_posts_titles = [i.text for i in browser.find_by_css(".post h2")]
        assert rendered_posts_titles == [
            i.title for i in posts[len(posts) - page - posts_per_page : len(posts) - page]
        ]
        if page < len(posts) - posts_per_page:
            pagination_element("Previous").click()


# def test_non_public_posts_are_highlited(
#         web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
#     """When posts are published they become visible in blog roll."""
#     pass


# def test_admin_panel_navigation(
#         web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
#     """When posts are published they become visible in blog roll."""
#     pass


# def test_breadcrumbs(
#         web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
#     """When posts are published they become visible in blog roll."""
#     pass
