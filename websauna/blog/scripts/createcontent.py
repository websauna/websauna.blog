"""Fill blog with dummy content.

Usage: ws-blog-createcontent [options] <config_uri>

-h --help            Show this screen.
--posts=<num>        Number of posts [default: 50]
--tags=<num>         Number of tags [default: 100]
--tags-min=<num>     Minimum number of tags on post [default: 3].
--tags-max=<num>     Maximum number of tags on post [default: 30].
--user=<email>       Use existing uses as content author. [default: user@foo.bar]

"""

# Standard Library
import random

# Thirdparty Library
from docopt import docopt
from pyramid.paster import bootstrap

# Websauna
from websauna.system.devop.cmdline import init_websauna
from websauna.system.http import Request
from websauna.system.user.utils import get_user_class

# Websauna's Blog Addon
from websauna.blog.testing import fakefactory


def get_or_create_user(request: Request, email: str):
    UserModel = get_user_class(request.registry)
    dbsession = request.dbsession
    user = dbsession.query(UserModel).filter_by(email=email).first()
    if user is None:
        user = fakefactory.AdminFactory(email=email, password="qwerty")
    return user


def create_content(
    posts_num: int,
    tags_num: int,
    tags_rel_min: int,
    tags_rel_max: int,
    config_uri: str,
    user_email: str,
):
    """Set up app and create content"""
    bootstrap(config_uri)  # why that does not happening in `init_websauna`?
    request = init_websauna(config_uri)
    fakefactory.DB_SESSION_PROXY.session = request.dbsession

    with request.tm:
        user = get_or_create_user(request, user_email)
        tags = fakefactory.TagFactory.create_batch(size=tags_num)
        posts = fakefactory.PostFactory.create_batch(
            size=posts_num,
            author=user,
            published_at=fakefactory.factory.Faker("date_between"),
            created_at=fakefactory.factory.Faker("date_between"),
            updated_at=fakefactory.factory.Faker("date_between"),
            state=fakefactory.factory.LazyFunction(lambda: random.choice(list(request.workflow.states))),
            tags=fakefactory.factory.LazyFunction(
                lambda: random.sample(tags, k=random.randint(tags_rel_min, tags_rel_max))
            ),
        )
    return {'user': user, 'tags': tags, 'posts': posts}


def main():
    arguments = docopt(__doc__)

    posts_num = int(arguments['--posts'])
    tags_num = int(arguments['--tags'])
    tags_rel_min = int(arguments['--tags-min'])
    tags_rel_max = int(arguments['--tags-max'])
    config_uri = arguments['<config_uri>']
    user_email = arguments['--user']

    data = create_content(posts_num, tags_num, tags_rel_min, tags_rel_max, config_uri, user_email)
    print(data)
