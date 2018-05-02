"""Websauna's blog addon."""

# Thirdparty Library
from pyramid.config import Configurator

# Websauna
from websauna.system import Initializer
from websauna.utils.autoevent import after
from websauna.utils.autoevent import bind_events


class AddonInitializer:
    """Configure Blog addon for websauna."""

    def __init__(self, config: Configurator) -> None:
        self.config = config

    @after(Initializer.configure_admin)
    def configure_admin(self):
        """Include admin views."""
        from . import admins
        from . import adminviews

        self.config.scan(admins)
        self.config.scan(adminviews)

    @after(Initializer.configure_templates)
    def configure_templates(self):
        """Include our package templates folder in Jinja 2 configuration."""
        self.config.add_jinja2_search_path("websauna.blog:templates", name=".html", prepend=False)
        from . import templatevars
        self.config.include(templatevars)

    def configure_workflow(self):
        """Include workflow"""
        from . import workflow
        self.config.registry.registerUtility(workflow.TinyWorkflow(self.config), workflow.IWorkflow)
        self.config.include(workflow)

    def configure_addon_views(self):
        """Configure views for your application.

        Let the config scanner to pick ``@simple_route`` definitions from
        scanned modules. Alternative you can call ``config.add_route()``
        and ``config.add_view()`` here.
        """

        self.config.add_route("blog_tag", "/blog/tag/{tag}", factory="websauna.blog.resources.blog_container_factory")
        self.config.add_route("blog", "/blog/*traverse", factory="websauna.blog.resources.blog_container_factory")

        from . import views
        self.config.scan(views)

        from . import rss
        self.config.scan(rss)

    def run(self):
        """Addon configuration.

        Run custom configuration steps and binds its configuration events
        listeners.
        """

        # This will make sure our initialization hooks are called later
        bind_events(self.config.registry.initializer, self)

        # Run our custom initialization code which does not have a good hook
        self.configure_addon_views()

        # Add workflow
        self.configure_workflow()


def includeme(config: Configurator):
    """Entry point for Websauna main app to include this addon.

    In the Initializer of your app you should have:

    .. code-block:: python

        def include_addons(self):
            # ...
            self.config.include("websauna.blog")

    """
    addon_init = AddonInitializer(config)
    addon_init.run()
