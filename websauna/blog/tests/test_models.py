def test_post_str(fakefactory):
    post = fakefactory.PostFactory()
    assert str(post) == post.title


def test_post_repr(fakefactory):
    post = fakefactory.PostFactory()
    assert repr(post) == "#{}: {}".format(post.id, post.title)


def test_tag_str(fakefactory):
    tag = fakefactory.TagFactory()
    assert str(tag) == tag.title


def test_tag_repr(fakefactory):
    tag = fakefactory.TagFactory()
    assert repr(tag) == "#{}: {}".format(tag.id, tag.title)
