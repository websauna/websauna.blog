"""Functional tests."""
# Thirdparty Library
import pytest
import requests
# Pyramid
import transaction


@pytest.mark.xfail(strict=True)
def test_blog_site_map(web_server: str, dbsession, fakefactory):
    """Sitemap view."""

    with transaction.manager:
        post = fakefactory.PostFactory()
        dbsession.expunge_all()

    resp = requests.get("{}/sitemap.xml".format(web_server))
    assert resp.status_code == 200
    assert "blog" in resp.text
    assert post.slug in resp.text  # TODO: blog's content is not listed in sitemap
