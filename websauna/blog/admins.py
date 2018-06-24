"""``websauna.blog`` addon's amdin views."""

# Websauna
from websauna.system.admin.modeladmin import ModelAdmin
from websauna.system.admin.modeladmin import model_admin
from websauna.system.crud import Base64UUIDMapper

# Websauna's Blog Addon
from websauna.blog.models import Post
from websauna.blog.models import Tag


@model_admin(traverse_id="blog-posts")
class PostAdmin(ModelAdmin):
    """Manage blog's posts."""

    title = "Blog posts"
    model = Post
    mapper = Base64UUIDMapper(mapping_attribute="id")

    class Resource(ModelAdmin.Resource):
        """Post resource for admin panel."""

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
