"""py.test testing functional fixtures"""

import pytest
import transaction
from websauna.utils.time import now

from websauna.blog.models import Post


@pytest.fixture
def unpublished_post_id(dbsession):
    with transaction.manager:
        post = Post()
        post.title = "Hello world"
        post.body = "All roads lead to Toholampi åäö"
        post.ensure_slug(dbsession)
        dbsession.add(post)
        dbsession.flush()
        return post.id

@pytest.fixture
def published_post_id(dbsession, unpublished_post_id):
    with transaction.manager:
        post = dbsession.query(Post).get(unpublished_post_id)
        post.published_at = now()
        return post.id
