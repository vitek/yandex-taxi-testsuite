import operator

from testsuite import matching


def test_any_list():
    assert matching.any_list == []
    assert matching.any_list == ['foo', 'bar']
    assert matching.any_list != ()

    assert matching.any_list == matching.any_list
    assert matching.AnyList() == matching.AnyList()


def test_list():
    pred = matching.ListOf(matching.any_string)
    assert pred == ['foo', 'bar']
    assert pred != ['foo', 1]
    assert pred != ('foo',)

    assert pred == pred
    assert pred == matching.ListOf(matching.any_string)
    assert pred != matching.ListOf(matching.any_integer)


def test_unordered_list():
    assert [1, 3, 2] == matching.unordered_list([3, 2, 1])
    assert [{'v': 'a'}, {'v': 'b'}] == matching.unordered_list(
        [
            {'v': 'b'},
            {'v': 'a'},
        ],
        key=operator.itemgetter('v'),
    )

    pred = matching.unordered_list([1, 2, 3])
    assert pred == pred
    assert pred == matching.unordered_list([3, 2, 1])
    assert pred != matching.unordered_list([1, 2, 4])

    assert pred != (1, 2, 3)
