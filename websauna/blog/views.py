"""Set of ``websauna.blog`` addon views that provide public UI."""

# Standard Library
import logging

# Thirdparty Library
from pyramid.view import view_config

# Websauna
from websauna.system.core.breadcrumbs import get_breadcrumbs
from websauna.system.core.views.redirect import redirect_view
from websauna.system.crud.paginator import DefaultPaginator
from websauna.system.http import Request

# Websauna's Blog Addon
from websauna.blog.models import Tag
from websauna.blog.resources import BlogContainer
from websauna.blog.resources import PostResource


logger = logging.getLogger(__name__)


@view_config(route_name="blog", context=BlogContainer, renderer="blog/blog_roll.html", permission="view")
def blog_roll(blog_container, request):
    """Blog index view.

    Page show a list of all blog posts that user/visitor has permission to see.
    Private posts are highlighted and listed first.
    """
    breadcrumbs = get_breadcrumbs(blog_container, request)

    # Get a hold to admin object so we can jump there
    resource_admin = request.admin["models"]["blog-posts"]

    paginator = DefaultPaginator()
    blog_posts = list(blog_container.get_posts())
    count = len(blog_posts)
    batch = paginator.paginate(blog_posts, request, count)

    return locals()


@view_config(route_name="blog_tag", renderer="blog/tag_roll.html", permission="view")
def tag_roll(blog_container: BlogContainer, request: Request):
    """Tag roll.

    Page show a list of all posts for a given tag.
    """

    tag = request.matchdict["tag"]
    tag = request.dbsession.query(Tag).filter_by(title=tag).first()
    current_view_url = request.url
    current_view_name = "Posts tagged {}".format(tag)
    breadcrumbs = get_breadcrumbs(
        blog_container, request, current_view_name=current_view_name, current_view_url=current_view_url
    )

    # Get a hold to admin object so we can jump there
    resource_admin = request.admin["models"]["blog-tags"]

    paginator = DefaultPaginator()
    tagged_posts = list(blog_container.get_posts_by_tag(tag) if tag else tuple())
    count = len(tagged_posts)
    batch = paginator.paginate(tagged_posts, request, count)

    return locals()


@view_config(route_name="blog", context=PostResource, renderer="blog/post.html", permission="view")
def blog_post(post_resource, request):
    """Single blog post."""

    breadcrumbs = get_breadcrumbs(post_resource, request)
    post = post_resource.post
    disqus_id = request.registry.settings.get("blog.disqus_id", "").strip()
    return locals()


#: Convenience redirect /blog -> /blog/
_redirect_blog = redirect_view("/blog", new_path="/blog/", status_code=302)
