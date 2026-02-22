from catechism.templatetags.catechism_tags import get_item


def test_get_item_existing():
    d = {'foo': 'bar', 'baz': 42}
    assert get_item(d, 'foo') == 'bar'
    assert get_item(d, 'baz') == 42


def test_get_item_missing():
    d = {'foo': 'bar'}
    assert get_item(d, 'missing') == ''


def test_get_item_non_dict():
    assert get_item('not a dict', 'key') == ''
    assert get_item(None, 'key') == ''
    assert get_item(42, 'key') == ''
