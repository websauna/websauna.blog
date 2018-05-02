"""Functional tests."""

# Thirdparty Library
import transaction
from splinter.driver import DriverAPI
from sqlalchemy.orm.session import Session

# Websauna's Blog Addon
from websauna.blog.testing.helpers import login_user


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
        tag = fakefactory.TagFactory()
        post = fakefactory.PostFactory(tags=[tag])
        fakefactory.PostFactory()
        dbsession.expunge_all()

    browser.visit(web_server + "/blog/tag/{}".format(tag.title))
    assert len(browser.find_by_css("div.post")) == 1
    assert browser.is_text_present(post.title)


def test_visitor_sees_only_published_posts_in_tag_roll(
    web_server: str, browser: DriverAPI, dbsession: Session, fakefactory
):
    """Visitors should not see unpublished posts in blog roll."""

    with transaction.manager:
        tag = fakefactory.TagFactory()
        fakefactory.PostFactory(state="private", tags=[tag])
        dbsession.expunge_all()

    browser.visit(web_server + "/blog/tag/{}".format(tag.title))
    assert browser.is_element_visible_by_css("#blog-no-posts")


def test_authors_sees_unpublished_they_own_posts_on_tag_roll(
    web_server: str, browser: DriverAPI, dbsession: Session, fakefactory
):

    with transaction.manager:
        user = fakefactory.UserFactory()
        tag = fakefactory.TagFactory()
        published_post = fakefactory.PostFactory(author=user, tags=[tag])
        unpublished_post = fakefactory.PostFactory(author=user, state="private", tags=[tag])
        fakefactory.PostFactory(state="private")
        dbsession.expunge_all()

    login_user(web_server, browser, user)

    browser.visit(web_server + "/blog/tag/{}".format(tag.title))

    # only one post should be listed
    assert len(browser.find_by_css("div.post")) == 2
    assert browser.is_text_present(published_post.title)
    assert browser.is_text_present(unpublished_post.title)


def test_managers_sees_unpublished_posts_on_tag_roll(
    web_server: str, browser: DriverAPI, dbsession: Session, fakefactory
):
    with transaction.manager:
        user = fakefactory.AdminFactory()
        tag = fakefactory.TagFactory()
        published_post = fakefactory.PostFactory(tags=[tag])
        unpublished_post = fakefactory.PostFactory(state="private", tags=[tag])
        dbsession.expunge_all()

    login_user(web_server, browser, user)

    browser.visit(web_server + "/blog/tag/{}".format(tag.title))

    # only one post should be listed
    assert len(browser.find_by_css("div.post")) == 2
    assert browser.is_text_present(published_post.title)
    assert browser.is_text_present(unpublished_post.title)


def test_tag_roll_pagination(web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
    """When posts exceed batch size, pagination is activated. Test that it's sane."""
    posts_per_page = 20
    with transaction.manager:
        tag = fakefactory.TagFactory()
        posts = fakefactory.PostFactory.create_batch(100, tags=[tag])
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

    # checking not disabled buttons (First and Previous)
    assert pagination_element("First")
    assert pagination_element("Previous")

    # checking disabled buttons (Next and Last)
    assert pagination_element("Next", disabled=True)
    assert pagination_element("Last", disabled=True)

    # navigating to the first page (checking that First works correctly)
    pagination_element("First").click()

    # checking if "next" works correctly
    posts_titles = set(i.title for i in posts)
    for page in range(0, len(posts), posts_per_page):
        rendered_posts_titles = set(i.text for i in browser.find_by_css(".post h2"))
        assert rendered_posts_titles.issubset(posts_titles)
        posts_titles -= rendered_posts_titles
        if page < len(posts) - posts_per_page:
            pagination_element("Next").click()

    # checking if "prev" works correctly
    posts_titles = set(i.title for i in posts)
    for page in range(0, len(posts), posts_per_page):
        rendered_posts_titles = set(i.text for i in browser.find_by_css(".post h2"))
        assert rendered_posts_titles.issubset(posts_titles)
        posts_titles -= rendered_posts_titles
        if page < len(posts) - posts_per_page:
            pagination_element("Previous").click()


# def test_breadcrumbs(
#         web_server: str, browser: DriverAPI, dbsession: Session, fakefactory):
#     """When posts are published they become visible in blog roll."""
#     pass
