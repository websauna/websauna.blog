"""``websauna.blog`` addon resources.

Resources main aim is to allow having decoupled views representation
logic, authorization logic, and DB mappings. Basically resources are a
glue for getting together all these things.

All resources must provide ``__acl__`` method.
"""

# Standard Library
import logging
from typing import Iterable

# Thirdparty Library
from sqlalchemy import case
from zope.interface import implementer

# Websauna
from websauna.compat.typing import List
from websauna.system.core.interfaces import IContainer
from websauna.system.core.root import Root
from websauna.system.core.traversal import Resource
from websauna.system.http import Request

# Websauna's Blog Addon
from websauna.blog.models import Post
from websauna.blog.models import Tag


logger = logging.getLogger(__name__)


class PostResource(Resource):
    """Wrap SQLAlchemy Post model to traversing resource."""

    def __init__(self, request: Request, post: Post) -> None:
        super(PostResource, self).__init__(request)
        self.post = post

    def get_title(self) -> str:
        """Post's title."""
        return self.post.title

    def get_body(self) -> str:
        """Post's body."""
        return self.post.body

    def get_excerpt(self) -> str:
        """Post's body."""
        return self.post.excerpt

    def get_heading_class(self) -> str:
        """Visually separate draft posts from published posts when viewing blog roll as admin."""
        return "" if self.post.state == self.request.workflow.public else "text-danger"

    def __acl__(self) -> List[tuple]:
        """Dynamically give blog-post permissions."""
        return self.request.workflow.resolve_acl(self.post)


@implementer(IContainer)
class BlogContainer(Resource):
    """Contains all posts, mounted at /blog/."""

    state = "public"

    def __acl__(self) -> List[tuple]:
        """Dynamically give blog permissions."""
        return self.request.workflow.resolve_acl(self)

    def get_title(self):
        """Blog's title."""
        title = self.request.registry.settings.get("blog.title", "Websauna blog")
        return title

    def wrap_post(self, post: Post) -> "PostResource":
        """Convert raw SQLAlchemy Post instance to traverse and permission
        aware PostResource with its public URL."""
        res = PostResource(self.request, post)
        return Resource.make_lineage(self, res, post.slug)

    def posts_list_query(self):
        """Return a posts query object with right ordering applied."""
        dbsession = self.request.dbsession
        query = dbsession.query(Post).order_by(
            case([(Post.state == self.request.workflow.private, 0)], else_=1),
            Post.published_at.desc(),
            Post.created_at.desc()
        )
        return query

    def get_viewable_posts(self, query):
        """Yield viewable post resources.

        Converts query's results into resources and yields ones that user
        has permission to view.
        """

        # TODO: replace with sql filter
        for resource in map(self.wrap_post, query):
            if self.request.has_permission("view", resource):
                yield resource

    def get_posts(self) -> Iterable[PostResource]:
        """List all posts in this folder.

        Posts are filtered out by effective permissions that user has.
        """
        query = self.posts_list_query()
        return self.get_viewable_posts(query)

    def get_posts_by_tag(self, tag: Tag) -> Iterable[PostResource]:
        """Lists all posts by a tag within the permissions of a current user."""
        return self.get_viewable_posts(tag.posts)

    def items(self):
        """Sitemap support."""
        for resource in self.get_posts():
            yield resource.__name__, resource

    def __getitem__(self, item: str) -> PostResource:
        """Traversing to blog post."""

        dbsession = self.request.dbsession
        obj = dbsession.query(Post).filter_by(slug=item).one_or_none()
        if not obj:
            raise KeyError()
        return self.wrap_post(obj)


def blog_container_factory(request) -> BlogContainer:
    """Set up __parent__ and __name__ pointers for BlogContainer required for traversal."""
    folder = BlogContainer(request)
    root = Root.root_factory(request)
    return Resource.make_lineage(root, folder, "blog")
