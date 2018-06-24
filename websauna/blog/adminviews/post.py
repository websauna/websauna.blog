"""Admin views and buttons for post."""

# Thirdparty Library
import colander
import deform
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

# Websauna
from websauna.system.admin import views as adminviews
from websauna.system.core import messages
from websauna.system.core.templatecontext import friendly_time
from websauna.system.core.viewconfig import view_overrides
from websauna.system.crud import listing
from websauna.system.crud.formgenerator import SQLAlchemyFormGenerator
from websauna.system.crud.views import ResourceButton
from websauna.system.crud.views import TraverseLinkButton
from websauna.system.form.sqlalchemy import UUIDModelSet
from websauna.system.http import Request
from websauna.utils.slug import SlugDecodeError
from websauna.utils.slug import slug_to_uuid
from websauna.utils.slug import uuid_to_slug
from websauna.utils.time import now

# Websauna's Blog Addon
from websauna.blog.admins import PostAdmin
from websauna.blog.adminviews.utils import slugify
from websauna.blog.models import Post
from websauna.blog.models import Tag
from websauna.blog.resources import blog_container_factory


@colander.deferred
def deferred_tags_widget(_, kw):
    """Select tags widget."""
    dbsession = kw["request"].dbsession
    vocab = [(uuid_to_slug(tag_id), title) for tag_id, title in dbsession.query(Tag.id, Tag.title).all()]
    return deform.widget.Select2Widget(values=vocab, multiple=True, tags=True, css_class="tags-select2w")


class TagCreationalUUIDModelSet(UUIDModelSet):
    """Allow create ``Tag`` objects on a fly."""

    def preprocess_cstruct_values(self, node, cstruct):
        """Decode tag's slug to uuid, in case if can't decode create a new Tag."""
        dbsession = self.get_dbsession(node)
        items = []
        for value in cstruct:
            try:
                uuid = slug_to_uuid(value)
            except SlugDecodeError:
                tag = Tag(title=value)
                dbsession.add(tag)
                dbsession.flush()
                uuid = tag.id
            items.append(uuid)
        return items


#: Fields that can be edited by a user. Create and edit forms fields.
POST_EDITABLE_FIELDS = [
    "title",
    colander.SchemaNode(
        colander.String(),
        name="excerpt",
        description=("Snippet of text shown in Google search," " blog roll and RSS feed. Keep in 1-2 sentences."),
        required=True,
    ),
    colander.SchemaNode(
        TagCreationalUUIDModelSet(model=Tag, match_column="id"), name="tags", widget=deferred_tags_widget, missing=None
    ),
    colander.SchemaNode(
        colander.String(),
        name="body",
        widget=deform.widget.RichTextWidget(options=(("browser_spellcheck", True), ("height", 480))),
        required=True,
    ),
]

#: Fields that are viewable for a user. View form fields.
POST_VIEWABLE_FIELDS = [
    "id",
    "created_at",
    "published_at",
    "updated_at",
    "slug",
    "state",
    "author",
] + POST_EDITABLE_FIELDS


def post_navigate_url_getter(request, resource):
    # TODO: move all strings to ENUMs
    return request.route_url("blog", traverse=resource.obj.slug)


def friendly_created_at(view, column, post):
    return friendly_time(jinja_ctx=None, context=post.created_at)


def friendly_published_at(view, column, post):
    return friendly_time(jinja_ctx=None, context=post.published_at)


@view_overrides(context=PostAdmin)
class PostListing(adminviews.Listing):
    """Show all blog posts."""

    table = listing.Table(
        columns=[
            listing.Column("title", "Title", navigate_url_getter=post_navigate_url_getter),
            listing.Column("state", "State"),
            listing.Column("created_at", "Created", getter=friendly_created_at),
            listing.Column("published_at", "Published", getter=friendly_published_at),
            listing.Column("author", "Author"),
            listing.ControlsColumn(name="Admin Actions"),
        ]
    )


@view_overrides(context=PostAdmin)
class PostAdd(adminviews.Add):
    form_generator = SQLAlchemyFormGenerator(includes=POST_EDITABLE_FIELDS)

    def add_object(self, obj):
        """Add final details to newly created post and save it to DB.

        That includes:
        * creating a slug for an post,
        * setting logged in user as an post author,
        * setting a default state to the post.

        """
        dbsession = self.context.get_dbsession()
        obj.author = self.request.user
        obj.state = self.request.workflow.default_state
        with dbsession.no_autoflush:
            obj.slug = slugify(obj.title, Post.slug, dbsession)
        dbsession.add(obj)
        dbsession.flush()


@view_overrides(context=PostAdmin.Resource)
class PostEdit(adminviews.Edit):
    form_generator = SQLAlchemyFormGenerator(includes=POST_EDITABLE_FIELDS)


@view_overrides(context=PostAdmin.Resource)
class PostShow(adminviews.Show):
    """Show blog post technical details."""

    form_generator = SQLAlchemyFormGenerator(includes=POST_VIEWABLE_FIELDS)

    @property
    def resource_buttons(self):
        """Customize buttons toolbar."""

        buttons = adminviews.Show.resource_buttons.copy()

        # View on site button
        view_on_site = ResourceButton(id="btn-view-on-site", name="View on site")

        def link_on_site(context, request):
            container = blog_container_factory(request)
            resource = container[context.get_object().slug]
            return request.resource_url(resource)

        buttons.append(view_on_site)
        view_on_site.get_link = link_on_site

        is_post_published = self.get_object().state == self.request.workflow.public
        change_publish_status = TraverseLinkButton(
            id="btn-{}-post".format("retract" if is_post_published else "publish"),
            name="Unpublish" if is_post_published else "Publish",
            view_name="retract_post" if is_post_published else "publish_post",
            template="crud/form_button.html",
        )
        buttons.append(change_publish_status)

        return buttons


@view_config(context=PostAdmin.Resource, name="publish_post", route_name="admin", request_method="POST")
def publish_post(context: PostAdmin.Resource, request: Request):
    post = context.get_object()
    has_changed = request.workflow.transit(request.workflow.publish_transition, post)
    if has_changed:
        post.published_at = now()
    messages.add(request, kind="info", msg="The post has been published.", msg_id="msg-published")
    # Back to show page
    return HTTPFound(request.resource_url(context, "show"))


@view_config(context=PostAdmin.Resource, name="retract_post", route_name="admin", request_method="POST")
def retract_post(context: PostAdmin.Resource, request: Request):
    post = context.get_object()
    request.workflow.transit(request.workflow.hide_transition, post)
    messages.add(request, kind="info", msg="The post has been retracted.", msg_id="msg-unpublished")
    # Back to show page
    return HTTPFound(request.resource_url(context, "show"))
