# Pyramid
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.security import Everyone

# Websauna
from websauna.blog.views import blog_container_factory


def test_unpublished(test_request, unpublished_post):
    """Unpublished blogs can be only viewed by users in admin group."""

    blog_container = blog_container_factory(test_request)
    post_resource = blog_container["hello-world"]
    policy = test_request.registry.queryUtility(IAuthorizationPolicy)

    assert not post_resource.post.published_at
    assert not policy.permits(post_resource, Everyone, "view")
    assert policy.permits(post_resource, "group:admin", "view")


def test_published(test_request, published_post):
    """Published posts can be viewed by everyone."""

    blog_container = blog_container_factory(test_request)
    post_resource = blog_container["hello-world"]
    policy = test_request.registry.queryUtility(IAuthorizationPolicy)

    assert post_resource.post.published_at
    assert policy.permits(post_resource, Everyone, "view")
