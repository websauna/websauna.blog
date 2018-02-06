"""This contains app entry point for running a demo site for this addon or running functional tests for this addon."""

# Websauna
import websauna.system


class Initializer(websauna.system.DemoInitializer):
    """A demo / test app initializer for testing addon websauna.blog."""

    def include_addons(self):
        """Include this addon in the configuration."""
        self.config.include("websauna.blog")

    def run(self):
        super(Initializer, self).run()
        # add demo
        self.config.add_jinja2_search_path('websauna.blog:demotemplates', name='.html', prepend=True)


def main(global_config, **settings):
    init = Initializer(global_config)
    init.run()
    return init.make_wsgi_app()
