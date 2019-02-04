"""Place your SQLAlchemy models in this file."""
# Standard Library
from typing import List

# SQLAlchemy
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as psql

from slugify import slugify

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
    post_id = sa.Column(psql.UUID(as_uuid=True), sa.ForeignKey("blog_post.id"), primary_key=True)

    #: Tag id. :class:`uuid.UUID`
    tag_id = sa.Column(psql.UUID(as_uuid=True), sa.ForeignKey("blog_tag.id"), primary_key=True)


class Post(Base):

    __tablename__ = ADDON_PREFIX + "post"

    id = sa.Column(psql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()"))

    created_at = sa.Column(UTCDateTime, default=now, nullable=False)

    #: When this post was made public. If this is set the post is considered to be public, otherwise it's only admin accessible draft.
    published_at = sa.Column(UTCDateTime, default=None, nullable=True)

    #: When this post wast last edited
    updated_at = sa.Column(UTCDateTime, nullable=True, onupdate=now)

    #: Human readable title
    title = sa.Column(sa.String(256), nullable=False)

    #: Shown in the blog roll, RSS feed
    excerpt = sa.Column(sa.Text(), nullable=False, default="")

    #: Full body text as Markdown, shown on the post page
    body = sa.Column(sa.Text(), nullable=False, default="")

    #: URL identifier string
    slug = sa.Column(sa.String(256), nullable=False, unique=True)

    #: Author name as plain text
    author = sa.Column(sa.String(256), nullable=True)

    #: List of post's tags. [:class:`~.Tag`, ...]
    tags = sa.orm.relationship("Tag", secondary=AssociationPostsTags.__tablename__, back_populates="posts")

    #: Mixed bag of all other properties
    other_data = sa.Column(NestedMutationDict.as_mutable(psql.JSONB), default=dict)

    # By default order latest posts first
    __mapper_args__ = {
        "order_by": created_at.desc()
    }

    def ensure_slug(self, dbsession) -> str:
        """Make sure post has a slug.

        Generate a slug based on the title, but only if blog post doesn't have one.

        :return: Generated slug as a string
        """

        assert self.title

        if self.slug:
            return

        for attempt in range(1, 100):

            generated_slug = slugify(self.title)
            if attempt >= 2:
                generated_slug += "-" + str(attempt)

            # Check for existing hit
            if not dbsession.query(Post).filter_by(slug=generated_slug).one_or_none():
                self.slug = generated_slug
                return self.slug

        raise RuntimeError("Could not generate slug for {}".format(self.title))

    def get_tag_list(self) -> List[str]:
        return self.tags


class Tag(Base):
    """Tag model."""

    __tablename__ = ADDON_PREFIX + "tag"

    #: Auto-generated post id. :class:`uuid.UUID`
    id = sa.Column(psql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True)

    #: Human readable title, tag's text. :class:`str`
    title = sa.Column(sa.String(256), unique=True, nullable=False)

    #: List of tag's tags. [:class:`~.Post`, ...]
    posts = sa.orm.relationship("Post", secondary=AssociationPostsTags.__tablename__, back_populates="tags", order_by=Post.published_at.desc())

    #: Logger efficient representation of model object.
    def __repr__(self) -> str:
        return "#<Tag {}>: {}".format(self.id, self.title)

    #: Human friendly representation of model object.
    def __str__(self) -> str:
        return self.title
