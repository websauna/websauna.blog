"""Admin interface views and buttons."""

# Standard Library
import string

# Pyramid
import colander
import deform
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

# Websauna
from websauna.system.admin.views import Add as DefaultAdd
from websauna.system.admin.views import Edit as DefaultEdit
from websauna.system.admin.views import Listing as DefaultListing
from websauna.system.admin.views import Show as DefaultShow
from websauna.system.core import messages
from websauna.system.core.viewconfig import view_overrides
from websauna.system.crud import listing
from websauna.system.crud.views import ResourceButton
from websauna.system.crud.views import TraverseLinkButton
from websauna.system.form.csrf import CSRFSchema
from websauna.system.form.resourceregistry import ResourceRegistry
from websauna.system.form.schema import dictify
from websauna.system.form.schema import objectify
from websauna.system.form.sqlalchemy import UUIDModelSet
from websauna.system.http import Request
from websauna.utils.time import now
from websauna.utils.slug import SlugDecodeError
from websauna.utils.slug import slug_to_uuid
from websauna.utils.slug import uuid_to_slug

from .admins import PostAdmin
from .admins import TagAdmin
from .models import Post
from .models import Tag
from .views import get_post_resource


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


@colander.deferred
def deferred_is_good_slug(node, kwargs):
    """Validation logic for the slug."""

    request = kwargs["request"]

    # Context is available on the edit form only
    context = kwargs.get("context")  # type: PostAdmin.Resource
    dbsession = request.dbsession

    if context:
        # Context is available on edit form only
        currently_edited_post = context.get_object()
    else:
        currently_edited_post = None

    def is_good_slug(node: colander.SchemaNode, value: str):
        """Ensure the user doesn't invalid non-sluglike characters."""
        allowed = string.ascii_lowercase + string.digits + "-" + "_"

        for c in value:
            if c not in allowed:
                raise colander.Invalid(node, "Slug contained invalid character: {}".format(c))

        # Catch double slug attempts here, otherwise we will get HTTP 500 due to SQL level error
        existing_post = dbsession.query(Post).filter_by(slug=value).one_or_none()
        if existing_post and (existing_post != currently_edited_post):
            raise colander.Invalid(node, "Slug already exists: {}".format(value))

    return is_good_slug


class PostSchema(CSRFSchema):
    """Form to add/edit blog posts"""

    title = colander.SchemaNode(colander.String(), required=True)

    author = colander.SchemaNode(colander.String(), description="The name of the author", required=True)

    slug = colander.SchemaNode(
        colander.String(),
        validator=deferred_is_good_slug,
        missing=None,
        description="Blog post URL identifier. Leave empty to automatically generate from title")

    excerpt = colander.SchemaNode(
        colander.String(),
        description="Snippet of text shown in Google search, blog roll and RSS feed. Keep in 1-2 sentences.",
        required=True,
        widget=deform.widget.TextAreaWidget(),)

    tags = colander.SchemaNode(
        TagCreationalUUIDModelSet(model=Tag, match_column="id"),
        widget=deferred_tags_widget,
        missing=None)

    body = colander.SchemaNode(
        colander.String(),
        description="Use Markdown formatting.",
        required=True,
        widget=deform.widget.TextAreaWidget(rows=40, css_class="body-text"))

    def dictify(self, obj: Post) -> dict:
        """Serialize SQLAlchemy model instance to nested dictionary appstruct presentation."""
        appstruct = dictify(self, obj)
        return appstruct

    def objectify(self, appstruct: dict, obj: Post):
        """Store the dictionary data from the form submission on the object."""
        objectify(self, appstruct, obj)


@view_overrides(context=PostAdmin)
class PostListing(DefaultListing):
    """Show all blog posts."""
    table = listing.Table(
        columns=[
            listing.Column("title", "Title"),
            listing.Column("created_at", "Created"),
            listing.Column("published_at", "Published"),
            listing.ControlsColumn()
        ]
    )


@view_overrides(context=PostAdmin)
class PostAdd(DefaultAdd):
    """User listing modified to show the user hometown based on geoip of last login IP."""

    def get_form(self):
        """Use hand written schema instead of autogenerated for adding new posts."""
        schema = PostSchema().bind(request=self.request)
        form = deform.Form(schema, buttons=self.get_buttons(), resource_registry=ResourceRegistry(self.request))
        return form

    def add_object(self, obj):
        """Add objects to transaction lifecycle and flush newly created object to persist storage to give them id."""
        dbsession = self.context.get_dbsession()
        # Make sure we autogenerate a slug
        obj.ensure_slug(dbsession)
        dbsession.add(obj)
        dbsession.flush()


class PostEditSchema(CSRFSchema):
    """Form to add/edit blog posts"""

    title = colander.SchemaNode(colander.String(), required=True)

    author = colander.SchemaNode(colander.String(), description="The name of the author", required=True)

    slug = colander.SchemaNode(
        colander.String(),
        validator=deferred_is_good_slug,
        missing=None,
        description="Blog post URL identifier. Leave empty to automatically generate from title")

    excerpt = colander.SchemaNode(
        colander.String(),
        description="Snippet of text shown in Google search, blog roll and RSS feed. Keep in 1-2 sentences.",
        required=True,
        widget=deform.widget.TextAreaWidget(),)

    tags = colander.SchemaNode(
        TagCreationalUUIDModelSet(model=Tag, match_column="id"),
        widget=deferred_tags_widget,
        missing=None)

    body = colander.SchemaNode(
        colander.String(),
        description="Use Markdown formatting.",
        required=True,
        widget=deform.widget.TextAreaWidget(rows=40, css_class="body-text"))

    published_at = colander.SchemaNode(colander.DateTime(), required=False)

    def dictify(self, obj: Post) -> dict:
        """Serialize SQLAlchemy model instance to nested dictionary appstruct presentation."""
        appstruct = dictify(self, obj)
        return appstruct

    def objectify(self, appstruct: dict, obj: Post):
        """Store the dictionary data from the form submission on the object."""
        objectify(self, appstruct, obj)


@view_overrides(context=PostAdmin.Resource)
class PostEdit(DefaultEdit):
    """User listing modified to show the user hometown based on geoip of last login IP."""

    def get_form(self):
        """Use hand written schema instead of autogenerated for adding new posts."""
        schema = PostEditSchema().bind(request=self.request, context=self.context)
        form = deform.Form(schema, buttons=self.get_buttons(), resource_registry=ResourceRegistry(self.request))
        return form


@view_overrides(context=PostAdmin.Resource, renderer="admin/post_show.html")
class PostShow(DefaultShow):
    """Show blog post technical details."""

    @property
    def resource_buttons(self):
        """Customize buttons toolbar."""

        buttons = DefaultShow.resource_buttons.copy()

        # View on site button
        view_on_site = ResourceButton(id="btn-view-on-site", name="View on site")

        def link_on_site(context, request):
            resource = get_post_resource(request, context.get_object().slug)
            return request.resource_url(resource)
        view_on_site.get_link = link_on_site
        buttons.append(view_on_site)

        # Publish button
        if not self.get_object().published_at:
            change_publish_status = TraverseLinkButton(id="btn-change-publish-status", name="Publish", view_name="change_publish_status")
        else:
            change_publish_status = TraverseLinkButton(id="btn-change-publish-status", name="Unpublish", view_name="change_publish_status")

        # This is a state changing action, so we want to do HTTP POST
        change_publish_status.template = "crud/form_button.html"
        buttons.append(change_publish_status)

        return buttons


@view_config(context=PostAdmin.Resource, name="change_publish_status", route_name="admin", request_method="POST")
def change_publish_status(context: PostAdmin.Resource, request: Request):
    """Change publish status."""

    post = context.get_object()
    if post.published_at:
        post.published_at = None
        messages.add(request, kind="info", msg="The post has been retracted.", msg_id="msg-unpublished")
    else:
        post.published_at = now()
        messages.add(request, kind="info", msg="The post has been published.", msg_id="msg-published")

    # Back to show page
    return HTTPFound(request.resource_url(context, "show"))


def tag_navigate_url_getter(request, resource):
    # TODO: move all strings to ENUMs
    return request.route_url("blog_tag", tag=resource.obj.title)


@view_overrides(context=TagAdmin)
class TagListing(DefaultListing):
    """Show blog tags."""

    table = listing.Table(
        columns=[
            listing.Column("title", "Title", navigate_url_getter=tag_navigate_url_getter),
            listing.ControlsColumn(name="Admin Actions"),
        ]
    )
