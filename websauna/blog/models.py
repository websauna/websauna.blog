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


class Post(Base):

    __tablename__ = "blog_post"

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

    #: Tags stored as comma separated string. Please note that in the long run this should be changed to JSONB list . This is now plain text due to simplicity of demostration.
    tags = sa.Column(sa.String(256), nullable=False, default="")

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
        return self.tags.split(",")
