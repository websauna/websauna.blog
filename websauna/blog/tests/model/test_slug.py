# Websauna
from websauna.blog.models import Post


def test_slugify(dbsession):
    """Make sure we can slugify even if there is an existing conflicting title."""

    post = Post()
    post.title = "Hello world"
    post.body = "All roads lead to Toholampi"
    assert post.ensure_slug(dbsession) == "hello-world"
    dbsession.add(post)
    dbsession.flush()

    post = Post()
    post.title = "Hello world"
    post.body = "All roads lead to Toholampi"
    assert post.ensure_slug(dbsession) == "hello-world-2"
    dbsession.add(post)
    dbsession.flush()
