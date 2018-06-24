"""Extra global template variables added by this addon."""

# Thirdparty Library
# Pyramid
from pyramid.events import BeforeRender

# Websauna's Blog Addon
from websauna.blog.resources import blog_container_factory


def blog_container(request):
    """Link to a term, # if not found."""
    return blog_container_factory(request)


def includeme(config):

    def on_before_render(event):
        request = event["request"]
        event["blog_container"] = blog_container(request)

    config.add_subscriber(on_before_render, BeforeRender)
