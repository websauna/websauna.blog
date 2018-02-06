"""Functional tests."""
import requests


def test_rss_feed(web_server: str, published_post_id):
    """Download RSS feed."""

    resp = requests.get("{}/blog/rss".format(web_server))
    assert resp.status_code == 200

    # We get title
    assert "Hello world" in resp.text

    # We get body
    assert "All roads lead to Toholampi åäö" in resp.text
    assert resp.headers["content-type"] == "application/rss+xml; charset=UTF-8"
