# Standard Library
import os.path
import sys
from unittest.mock import patch

# Websauna's Blog Addon
import websauna.blog
from websauna.blog.scripts.createcontent import create_content
from websauna.blog.scripts.createcontent import main


def test_createcontent(dbsession):
    config_file = os.path.join(os.path.dirname(os.path.abspath(websauna.blog.__file__)), "conf", "test.ini")
    params = dict(
        posts_num=1,
        tags_num=2,
        tags_rel_min=1,
        tags_rel_max=2,
        config_uri=config_file,
        user_email='max@max.max'
    )
    data = create_content(**params)
    assert data['user']
    assert data['tags']
    assert data['posts']
    create_content(**params)  # coverage


def test_cli(dbsession):
    testargs = ['', 'sad']
    with patch("websauna.blog.scripts.createcontent.create_content") as mock, patch.object(sys, 'argv', testargs):
        main()
    mock.assert_called_once_with(50, 100, 3, 30, 'sad', 'user@foo.bar')
