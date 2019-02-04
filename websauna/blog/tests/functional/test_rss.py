"""Functional tests."""
import requests
import transaction


def test_rss_feed(web_server: str, fakefactory, dbsession):
    """Download RSS feed."""

    with transaction.manager:
        post = fakefactory.PostFactory(public=True)
        dbsession.expunge_all()

    resp = requests.get("{}/blog/rss".format(web_server))
    assert resp.status_code == 200

    # We get title
    assert post.title in resp.text

    # We get body
    assert post.excerpt in resp.text
    assert resp.headers["content-type"] == "application/rss+xml; charset=UTF-8"
