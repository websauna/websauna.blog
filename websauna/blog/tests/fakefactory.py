"""Factories for creating dummy content objects."""

# Standard Library
from uuid import uuid4
from random import randint

# Pyramid
from pyramid.threadlocal import get_current_registry

import factory

# Websauna
from websauna.blog import models
from websauna.system.user import models as ws_models
from websauna.system.user.interfaces import IPasswordHasher
from websauna.utils.time import now


class DBSessionProxy:
    """Proxy for attaching the right sqlachemy's session to the fake-factories.

    ``factory_boy`` requires sqlachemy's session to be defined on fake-factories
    at declaration stage, but ``websauna`` creates the session at the late
    configuration stage and newer exposes it as global variable. This proxy
    allows the session to be attached to the fake-factories by tests or fixtures.
    """
    session = None

    def __getattr__(self, attr):
        return getattr(self.session, attr)


DB_SESSION = DBSessionProxy()


def hash_password(password: str):
    """Transform password into hash"""

    registry = get_current_registry()
    hasher = registry.getUtility(IPasswordHasher)
    hashed = hasher.hash_password(password)
    return hashed


def ensure_admin_group_returned():
    """Return admin group. If the group doesn't exist then create it."""

    admin_group = (
        DB_SESSION.query(ws_models.Group).filter_by(name=ws_models.Group.DEFAULT_ADMIN_GROUP_NAME).first()
    )
    if admin_group is None:
        admin_group = GroupFactory(name=ws_models.Group.DEFAULT_ADMIN_GROUP_NAME)
    return admin_group


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Base factory for working session."""

    class Meta:
        sqlalchemy_session = DB_SESSION
        sqlalchemy_session_persistence = 'flush'
        abstract = True


class GroupFactory(BaseFactory):
    """Factory for creating dummy Groups."""

    name = factory.Faker("slug")

    class Meta:
        model = ws_models.Group


class UserFactory(BaseFactory):
    """Factory for creating dummy Users."""

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    hashed_password = factory.LazyAttribute(lambda obj: hash_password(obj.password))
    activated_at = factory.LazyAttribute(lambda obj: now())

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Ensure that newly created user can log in."""
        user = super()._create(model_class, *args, **kwargs)
        assert user.can_login()
        return user

    class Meta:
        model = ws_models.User
        exclude = ("password",)

    class Params:
        password = "qwerty"

        #: Trait for creating admin users
        admin = factory.Trait(
            groups=factory.LazyAttribute(lambda obj: [ensure_admin_group_returned()]),
        )


class PostFactory(BaseFactory):
    """Factory for creating dummy Posts."""

    title = factory.Faker("catch_phrase")
    excerpt = factory.Faker("sentence")
    body = factory.Faker("text", max_nb_chars=2000)
    author = factory.Faker('name')
    slug = factory.LazyAttribute(lambda obj: uuid4().hex)
    created_at = factory.Faker('date_this_decade')
    tags = factory.LazyFunction(lambda: [TagFactory() for i in range(randint(1, 6))])

    class Meta:
        model = models.Post

    class Params:

        #: Trait for creating public posts
        public = factory.Trait(
            published_at=factory.LazyAttribute(lambda obj: now())
        )

        #: Trait for creating private posts
        private = factory.Trait(
            published_at=None
        )


class TagFactory(BaseFactory):
    """Factory for creating dummy Posts."""

    title = factory.Faker("slug")

    class Meta:
        model = models.Tag
