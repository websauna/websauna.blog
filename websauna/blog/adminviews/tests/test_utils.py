# Standard Library
from unittest.mock import MagicMock

# Thirdparty Library
import pytest
import transaction

# Websauna's Blog Addon
from websauna.blog.adminviews.utils import slugify
from websauna.blog.models import Post


def test_slugify(dbsession):
    assert slugify("Hello world", Post.slug, dbsession) == "hello-world"


def test_slugify_too_long(dbsession):
    """ len shit"""
    assert len(slugify("a" * 1000, Post.slug, dbsession)) == 254


def test_slugify_spin(dbsession, fakefactory):
    slug = "aaaaaaaaaa"
    with transaction.manager:
        fakefactory.PostFactory(title=slug)
    assert slugify(slug, Post.slug, dbsession) == slug + "-1"


def test_slugify_was_not_to_generate(dbsession, fakefactory):
    uniqueness_checker = MagicMock(return_value=True)
    with pytest.raises(RuntimeError):
        assert slugify("a", None, None, MagicMock(return_value=3), uniqueness_checker=uniqueness_checker)
    assert uniqueness_checker.call_count == 99
