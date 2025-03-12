from testsuite import matching


def test_any_dict():
    assert matching.any_dict == {}
    assert matching.any_dict == {'foo': 'bar'}
    assert matching.any_dict != []

    assert matching.any_dict == matching.any_dict
    assert matching.AnyDict() == matching.AnyDict()


def test_dict_of():
    pred = matching.DictOf(value=matching.any_string)
    assert pred == {'foo': 'bar'}
    assert pred != {'foo': 1}

    pred = matching.DictOf(key=matching.any_string)
    assert pred == {'foo': 'bar'}
    assert pred != {1: 'bar'}

    dict1 = matching.DictOf(matching.any_string, matching.any_integer)
    dict2 = matching.DictOf(matching.any_string, matching.any_integer)
    dict3 = matching.DictOf(matching.any_string, matching.any_string)

    assert dict1 == dict2
    assert dict != dict3


def test_partial_dict():
    sample = {
        'some_int': 1,
        'some_str': 'abc',
        'some_dict': {'a': 5, 'b': 'b', 'c': 6},
    }

    assert sample == matching.PartialDict(some_int=1)
    assert sample == matching.PartialDict(some_int=1, some_str='abc')
    assert sample == matching.PartialDict(
        some_int=1,
        some_str='abc',
        some_dict=matching.PartialDict(a=5),
    )

    assert sample != matching.PartialDict(some_int=2)
    assert sample != matching.PartialDict(unknown=3)
    assert sample != matching.PartialDict(
        some_int=1,
        some_str='abc',
        some_dict=matching.PartialDict(a=123, asd=55),
    )

    assert matching.PartialDict() != 5

    assert sample == matching.PartialDict({'some_int': 1})

    assert sample == matching.PartialDict(some_int=1)
    assert not (sample != matching.PartialDict(some_int=1))


def test_partial_dict_instances():
    assert matching.PartialDict(foo=1) == matching.PartialDict(foo=1)
    assert matching.PartialDict(foo=1) == matching.PartialDict(foo=1, bar=2)
    assert matching.PartialDict(foo=1, bar=2) == matching.PartialDict(foo=1)

    assert matching.PartialDict(foo=1) != matching.PartialDict(foo=2)
