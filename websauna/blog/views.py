# Standard Library
import logging
from typing import Iterable

# Pyramid
from pyramid.decorator import reify
from pyramid.security import Allow
from pyramid.security import Deny
from pyramid.security import Everyone
from pyramid.view import view_config
from zope.interface import implementer

import markdown

# Websauna
from websauna.compat.typing import List
from websauna.system.core.breadcrumbs import get_breadcrumbs
from websauna.system.core.interfaces import IContainer
from websauna.system.core.root import Root
from websauna.system.core.traversal import Resource
from websauna.system.core.views.redirect import redirect_view
from websauna.system.crud.paginator import DefaultPaginator

from websauna.system.http import Request

from .models import Post


logger = logging.getLogger(__name__)


class PostResource(Resource):
    """Wrap SQLAlchemy Post model to traversing resource."""

    def __init__(self, request: Request, post: Post):
        super(PostResource, self).__init__(request)
        self.post = post

    def get_title(self) -> str:
        return self.post.title

    def get_body_as_html(self) -> str:
        return markdown.markdown(self.post.body)

    def get_heading_class(self) -> str:
        """Visually separate draft posts from published posts when viewing blog roll as admin."""

        if self.post.published_at:
            return ""
        else:
            return "text-danger"

    @reify
    def __acl__(self) -> List[tuple]:
        """Dynamically give blog post permissions."""

        # Only published posts are viewable to the audience
        if self.post.published_at:
            return [
                (Allow, Everyone, "view"),
            ]
        else:
            # Draft post
            return [
                (Allow, "group:admin", "view"),  # Only show drafts/previews for admin
                (Deny, Everyone, "view"),
            ]


@implementer(IContainer)
class BlogContainer(Resource):
    """Contains all posts, mounted at /blog/."""

    __acl__ = [
        (Allow, "group:admin", "edit"),  # Needed to render admin edit links in main UI
    ]

    def get_title(self):
        title = self.request.registry.settings.get("blog.title", "Websauna blog")
        return title

    def wrap_post(self, post: Post) -> "PostResource":
        """Convert raw SQLAlchemy Post instance to traverse and permission aware PostResource with its public URL."""
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

    def get_posts_by_tag(self, tag: str) -> Iterable[PostResource]:
        """Lists all posts by a tag within the permissions of a current user."""
        for resource in self.get_posts():
            if tag in resource.post.get_tag_list():
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

    def get_published_posts(self, limit=5) -> Iterable[PostResource]:
        """Iterate all published posts in this folder."""

        dbsession = self.request.dbsession
        q = dbsession.query(Post).filter(Post.published_at != None).order_by(Post.published_at.desc())  # noQA

        for post in q.all()[0:limit]:
            resource = self.wrap_post(post)
            yield resource

    def __getitem__(self, item: str) -> PostResource:
        """Traversing to blog post."""

        dbsession = self.request.dbsession
        item = dbsession.query(Post).filter_by(slug=item).one_or_none()
        if item:
            return self.wrap_post(item)

        raise KeyError()


def blog_container_factory(request) -> BlogContainer:
    """Set up __parent__ and __name__ pointers for BlogContainer required for traversal."""
    folder = BlogContainer(request)
    root = Root.root_factory(request)
    return Resource.make_lineage(root, folder, "blog")


@view_config(route_name="blog", context=BlogContainer, name="", renderer="blog/blog_roll.html")
def blog_roll(blog_container, request):
    """Blog index view."""
    breadcrumbs = get_breadcrumbs(blog_container, request)

    # Get a hold to admin object so we can jump there
    post_admin = request.admin["models"]["blog-posts"]
    paginator = DefaultPaginator()
    blog_posts = list(blog_container.get_roll_posts())
    count = len(blog_posts)
    batch = paginator.paginate(blog_posts, request, count)

    return locals()


@view_config(route_name="blog_tag", renderer="blog/tag_roll.html")
def tag(blog_container: BlogContainer, request: Request):
    """Tag roll."""

    tag = request.matchdict["tag"]
    current_view_url = request.url
    current_view_name = "Posts tagged {}".format(tag)
    breadcrumbs = get_breadcrumbs(blog_container, request, current_view_name=current_view_name, current_view_url=current_view_url)

    # Get a hold to admin object so we can jump there
    post_admin = request.admin["models"]["blog-posts"]

    paginator = DefaultPaginator()
    tagged_posts = list(blog_container.get_posts_by_tag(tag))
    count = len(tagged_posts)
    batch = paginator.paginate(tagged_posts, request, count)

    return locals()


@view_config(route_name="blog", context=PostResource, name="", renderer="blog/post.html")
def blog_post(post_resource, request):
    """Single blog post."""
    breadcrumbs = get_breadcrumbs(post_resource, request)
    post = post_resource.post
    disqus_id = request.registry.settings.get("blog.disqus_id", "").strip()
    return locals()


def get_post_resource(request: Request, slug: str) -> PostResource:
    """Helper function to get easily URL mapped blog posts."""

    container = blog_container_factory(request)
    try:
        return container[slug]
    except KeyError:
        return None


# Convenience redirect /blog -> /blog/
_redirect = redirect_view("/blog", new_path="/blog/", status_code=302)
