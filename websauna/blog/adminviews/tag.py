"""Admin views and buttons for tag."""

# Websauna
from websauna.system.admin import views as adminviews
from websauna.system.core.viewconfig import view_overrides
from websauna.system.crud import listing

# Websauna's Blog Addon
from websauna.blog.admins import TagAdmin


def tag_navigate_url_getter(request, resource):
    # TODO: move all strings to ENUMs
    return request.route_url("blog_tag", tag=resource.obj.title)


@view_overrides(context=TagAdmin)
class PostListing(adminviews.Listing):
    """Show blog tags."""

    table = listing.Table(
        columns=[
            listing.Column("title", "Title", navigate_url_getter=tag_navigate_url_getter),
            listing.ControlsColumn(name="Admin Actions"),
        ]
    )
