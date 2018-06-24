# Pyramid
# Thirdparty Library
# Thirdparty Library
# Thirdparty Library
# Thirdparty Library
import transaction
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.security import Everyone

# Websauna's Blog Addon
from websauna.blog.resources import blog_container_factory


def test_unpublished(test_request, fakefactory, dbsession):

    """Unpublished blogs can be only viewed by users in admin group."""

    with transaction.manager:
        post = fakefactory.PostFactory(state="private")
        dbsession.expunge_all()

    blog_container = blog_container_factory(test_request)
    post_resource = blog_container[post.slug]
    policy = test_request.registry.queryUtility(IAuthorizationPolicy)

    assert not policy.permits(post_resource, Everyone, "view")
    assert policy.permits(post_resource, "group:admin", "view")


def test_published(test_request, fakefactory, dbsession):
    """Published posts can be viewed by everyone."""
    with transaction.manager:
        post = fakefactory.PostFactory()
        dbsession.expunge_all()

    blog_container = blog_container_factory(test_request)
    post_resource = blog_container[post.slug]
    policy = test_request.registry.queryUtility(IAuthorizationPolicy)

    assert post_resource.post.published_at
    assert policy.permits(post_resource, Everyone, "view")
