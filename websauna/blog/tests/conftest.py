"""py.test testing fixtures"""

import pytest
from websauna.utils.time import now

from ..models import Post


@pytest.fixture
def unpublished_post(dbsession):
    post = Post()
    post.title = "Hello world"
    post.body = "All roads lead to Toholampi"
    post.ensure_slug(dbsession)
    dbsession.add(post)
    dbsession.flush()
    return post


@pytest.fixture
def published_post(unpublished_post):
    unpublished_post.published_at = now()
    return unpublished_post