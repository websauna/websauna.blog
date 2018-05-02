"""``websauna.blog`` models.

DB relation model:

.. uml::

    @startuml
    left to right direction
    User --{ Post
    Post --{ AssociationPostsTags
    Tag --{ AssociationPostsTags
    @enduml

"""

# Thirdparty Library
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as psql

# Websauna
from websauna.system.model.columns import UTCDateTime
from websauna.system.model.json import NestedMutationDict
from websauna.system.model.meta import Base
from websauna.utils.time import now


ADDON_PREFIX = 'blog_'


class AssociationPostsTags(Base):
    """Model to associate ``posts`` with ``tags``."""

    __tablename__ = ADDON_PREFIX + "association_posts_tags"

    #: Post id. :class:`uuid.UUID`
    post_id = sa.Column(psql.UUID(as_uuid=True), sa.ForeignKey("blog_posts.id"), primary_key=True)

    #: Tag id. :class:`uuid.UUID`
    tag_id = sa.Column(psql.UUID(as_uuid=True), sa.ForeignKey("blog_tags.id"), primary_key=True)


class Post(Base):
    """Post model."""

    __tablename__ = ADDON_PREFIX + "posts"

    #: Auto-generated post id. :class:`uuid.UUID`
    id = sa.Column(psql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()"))

    #: When post was created. :class:`UTCDateTime <websauna.system.model.columns.UTCDateTime>`
    created_at = sa.Column(UTCDateTime, default=now, nullable=False)

    #: When post was made public. :class:`UTCDateTime <websauna.system.model.columns.UTCDateTime>`
    published_at = sa.Column(UTCDateTime, default=None, nullable=True)

    #: When post wast last edited. :class:`UTCDateTime <websauna.system.model.columns.UTCDateTime>`
    updated_at = sa.Column(UTCDateTime, nullable=True, onupdate=now)

    #: Post's state, based on this value ``workflow`` determinate post's ``ACL``.
    #:  Basically, field makes post public or private. :class:`str`
    state = sa.Column(sa.String(128), nullable=False, default="private", index=True)

    #: Human readable title. :class:`str`
    title = sa.Column(sa.String(256), nullable=False)

    #: Shown in the blog roll, RSS feed. :class:`str`
    excerpt = sa.Column(sa.Text(), nullable=False, default="")

    #: Full body text, shown on the post page. :class:`str`
    body = sa.Column(sa.Text(), nullable=False, default="")

    #: URL identifier string. :class:`str`
    slug = sa.Column(sa.String(256), nullable=False, unique=True)

    #: Post's author. :class:`User <websauna.system.user.models.User>`
    author = sa.orm.relationship("User")
    author_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))

    #: List of post's tags. [:class:`~.Tag`, ...]
    tags = sa.orm.relationship("Tag", secondary=AssociationPostsTags.__tablename__, back_populates="posts")

    #: Mixed ``jsonb`` bag of all other properties. :class:`dict`
    other_data = sa.Column(NestedMutationDict.as_mutable(psql.JSONB), default=dict)

    # By default order latest posts first
    __mapper_args__ = {"order_by": created_at.desc()}

    #: Logger efficient representation of model object.
    def __repr__(self) -> str:
        return "#{}: {}".format(self.id, self.title)

    #: Human friendly representation of model object.
    def __str__(self) -> str:
        return self.title


class Tag(Base):
    """Tag model."""

    __tablename__ = ADDON_PREFIX + "tags"

    #: Auto-generated post id. :class:`uuid.UUID`
    id = sa.Column(psql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True)

    #: Human readable title, tag's text. :class:`str`
    title = sa.Column(sa.String(256), unique=True, nullable=False)

    #: List of tag's tags. [:class:`~.Post`, ...]
    posts = sa.orm.relationship("Post", secondary=AssociationPostsTags.__tablename__, back_populates="tags")

    #: Logger efficient representation of model object.
    def __repr__(self) -> str:
        return "#{}: {}".format(self.id, self.title)

    #: Human friendly representation of model object.
    def __str__(self) -> str:
        return self.title
