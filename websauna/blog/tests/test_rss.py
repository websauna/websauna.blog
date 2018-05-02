"""Functional tests."""
# Thirdparty Library
import requests
# Pyramid
import transaction


def test_rss_feed(web_server: str, dbsession, fakefactory):
    """Download RSS feed."""

    with transaction.manager:
        post = fakefactory.PostFactory()
        dbsession.expunge_all()

    resp = requests.get("{}/blog/rss".format(web_server))
    assert resp.status_code == 200

    # We get title
    assert post.title in resp.text

    # We get body
    assert post.excerpt in resp.text
    assert resp.headers["content-type"] == "application/rss+xml; charset=UTF-8"


def test_rss_private_posts(web_server: str, dbsession, fakefactory):
    with transaction.manager:
        post = fakefactory.PostFactory(state="private")
        dbsession.expunge_all()

    resp = requests.get("{}/blog/rss".format(web_server))
    assert resp.status_code == 200

    # We get title
    assert post.title not in resp.text

    # We get body
    assert post.excerpt not in resp.text
    assert resp.headers["content-type"] == "application/rss+xml; charset=UTF-8"
