
# Websauna
from websauna.system.admin.modeladmin import ModelAdmin
from websauna.system.admin.modeladmin import model_admin
from websauna.system.crud import Base64UUIDMapper

from .models import Post
from .models import Tag


@model_admin(traverse_id="blog-posts")
class PostAdmin(ModelAdmin):
    """Manage user owned accounts and their balances."""

    title = "Blog posts"

    model = Post

    # UserOwnedAccount.id attribute is uuid type
    mapper = Base64UUIDMapper(mapping_attribute="id")

    class Resource(ModelAdmin.Resource):

        # Get something human readable about this object to the breadcrumbs bar
        def get_title(self):
            return self.get_object().title


@model_admin(traverse_id="blog-tags")
class TagAdmin(ModelAdmin):
    """Manage blog's tags."""

    title = "Blog tags"
    model = Tag
    mapper = Base64UUIDMapper(mapping_attribute="id")

    class Resource(ModelAdmin.Resource):
        """Tag resource for admin panel."""

        def get_title(self):
            return self.get_object().title
