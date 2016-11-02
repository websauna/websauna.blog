from typing import Iterable, Optional
import logging

import markdown
from pyramid.decorator import reify
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.security import Allow, Deny
from pyramid.security import Everyone
from pyramid.view import view_config
from zope.interface import implementer

from websauna.system.core.breadcrumbs import get_breadcrumbs
from websauna.system.core.interfaces import IContainer
from websauna.system.core.root import Root
from websauna.system.core.traversal import Resource
from websauna.system.http import Request
from websauna.compat.typing import List

from .models import Post


logger = logging.getLogger(__name__)


class PostResource(Resource):
    """Wrap SQLAlchemy Post model to traversing resource."""

    def __init__(self, request: Request, post: Post):
        super(PostResource, self).__init__(request)
        self.post = post

    def get_title(self) -> str:
        return self.post.title

    def get_excerpt_as_html(self) -> str:
        return markdown.markdown(self.post.excerpt)

    @reify
    def __acl__(self) -> List[tuple]:
        """Dynamically give blog post permissions."""

        # Only publised posts are viewable to the audience
        if self.post.published_at:
            return [
                (Allow, Everyone, "view")
            ]
        else:
            # Unpublished
            return [
                (Deny, Everyone, "view"),
                (Allow, "group:admin", "view"),
            ]


@implementer(IContainer)
class BlogContainer(Resource):
    """Contains all posts."""

    def get_title(self):
        return "Blog"

    def wrap_post(self, post: Post) -> "PostResource":
        res = PostResource(self.request, post)
        return Resource.make_lineage(self, res, post.slug)

    def get_posts(self) -> Iterable[PostResource]:
        """List all posts in this folder.

        We filter out by current user permissions.
        """

        dbsession = self.request.dbsession
        q = dbsession.query(Post).order_by(Post.published_at.desc())

        for post in q:
            resource = self.wrap_post(post)
            if self.request.has_permission("view", resource):
                yield resource

    def items(self):
        """Sitemap support."""
        for resource in self.get_posts():
            yield resource.__name__, resource

    def get_roll_posts(self) -> List[PostResource]:
        """Get all blog posts.

        We return a list instead of iterator, so we can test for empty blog condition in templates.
        """
        return list(self.get_posts())

    def __getitem__(self, item):
        """Traversing to blog post."""
        dbsession = self.request.dbsession
        item = dbsession.query(Post).filter_by(slug=item).one_or_none()
        if item:
            return self.wrap_post(item)
        raise KeyError()


def blog_container_factory(request) -> BlogContainer:
    """Set up __parent__ and __name__ pointers required for traversal."""
    folder = BlogContainer(request)
    root = Root.root_factory(request)
    return Resource.make_lineage(root, folder, "blog")


@view_config(route_name="blog", context=BlogContainer, name="", renderer="blog/blog_roll.html")
def blog_roll(blog_container, request):
    """Blog root view."""
    breadcrumbs = get_breadcrumbs(blog_container, request)
    title = request.registry.settings.get("blog_title", "Websauna blog")
    return locals()


@view_config(route_name="blog", context=BlogContainer, name="rss", renderer="blog/rss.xml")
def blog_feed(blog_container, request):
    """RSS feed for the blog."""
    return locals()


@view_config(route_name="blog", context=PostResource, name="", renderer="blog/post.html")
def blog_post(res, request):
    """View post."""
    breadcrumbs = get_breadcrumbs(res, request)
    post = res.post

    # Format markdown
    body = markdown.markdown(post.body)
    return locals()


def get_post_resource(request: Request, slug: str) -> PostResource:
    """Helper function to get easily URL mapped blog posts."""

    container = blog_container_factory(request)
    try:
        return container[slug]
    except KeyError:
        return None