# Thirdparty Library
from slugify import slugify as base_slugify


def get_field_allowed_length(field):
    return getattr(field.class_.__table__.c, field.key).type.length


def is_slug_already_exists(dbsession, field, slug):
    return bool(dbsession.query(field.class_).filter(field == slug).one_or_none())


def slugify(
    text, field, dbsession, max_length_getter=get_field_allowed_length, uniqueness_checker=is_slug_already_exists
):
    """DB model aware slugify.

    A slugify with some extra:
    * adjust generated slug length to field max allowed length if it's exited.
    * ensure slug uniqueness (optional)
    """
    for i in range(99):
        unifier = "-{}".format(i)
        slug = base_slugify(text, max_length=max_length_getter(field) - len(unifier))
        slug += unifier if i else ""
        if uniqueness_checker and not uniqueness_checker(dbsession, field, slug):
            break
    else:
        raise RuntimeError("Wasn't able to generate slug")
    return slug
