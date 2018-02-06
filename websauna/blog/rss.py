"""RSS feed generation and serving.

See https://github.com/svpino/rfeed
"""

# Pyramid
from pyramid.response import Response
from pyramid.view import view_config

import rfeed

# Websauna
from websauna.utils.time import now

from .views import BlogContainer
from .views import PostResource


class Content(rfeed.Extension):

    def get_namespace(self):
        return {"xmlns:content": "http://purl.org/rss/1.0/modules/content/"}


class ContentItem(rfeed.Serializable):

    def __init__(self, post_resource: PostResource):
        super(ContentItem, self).__init__()
        self.post_resource = post_resource

    def publish(self, handler):
        super(ContentItem, self).publish(handler)
        html = self.post_resource.get_body_as_html()
        self._write_element("content:encoded", html)


def generate_rss(blog_container: BlogContainer):
    """Generate RSS feed using rfeed"""

    request = blog_container.request
    blog_title = request.registry.settings.get("blog.title")
    blog_email = request.registry.settings.get("blog.rss_feed_email", "no-reply@example.com")

    items = []
    for post_resource in blog_container.get_posts():
        post = post_resource.post
        item = rfeed.Item(
            title=post.title,
            link=request.resource_url(post_resource),
            description="This is the description of the first article",
            author=blog_email,
            creator=post.author,
            guid=rfeed.Guid(str(post.id)),
            pubDate=post.published_at,
            extensions=[ContentItem(post_resource)])
        items.append(item)

    feed = rfeed.Feed(
        title=blog_title,
        link=request.resource_url(blog_container, "rss"),
        description="",
        language="en-US",
        lastBuildDate=now(),
        items=items,
        extensions=[Content()])

    return feed


@view_config(route_name="blog", context=BlogContainer, name="rss")
def blog_feed(blog_container, request):
    """RSS feed for the blog."""
    feed = generate_rss(blog_container)
    return Response(body=feed.rss(), content_type="application/rss+xml")
