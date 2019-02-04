# Pyramid
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.security import Everyone

# Websauna
from websauna.blog.views import blog_container_factory
import transaction


def test_unpublished(test_request, fakefactory, dbsession):
    """Unpublished blogs can be only viewed by users in admin group."""

    with transaction.manager:
        post = fakefactory.PostFactory(private=True)
        dbsession.expunge_all()

    blog_container = blog_container_factory(test_request)
    post_resource = blog_container[post.slug]
    policy = test_request.registry.queryUtility(IAuthorizationPolicy)

    assert not post_resource.post.published_at
    assert not policy.permits(post_resource, Everyone, "view")
    assert policy.permits(post_resource, "group:admin", "view")


def test_published(test_request, fakefactory, dbsession):
    """Published posts can be viewed by everyone."""

    with transaction.manager:
        post = fakefactory.PostFactory(public=True)
        dbsession.expunge_all()

    blog_container = blog_container_factory(test_request)
    post_resource = blog_container[post.slug]
    policy = test_request.registry.queryUtility(IAuthorizationPolicy)

    assert post_resource.post.published_at
    assert policy.permits(post_resource, Everyone, "view")
