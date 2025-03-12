from testsuite import matching


def test_or():
    assert matching.Or(1, 2) == 1
    assert matching.Or(1, 2) == 2
    assert matching.Or(1, 2) != 3
    assert matching.Or(1, 2) != 'foo'

    pred = matching.Or(1, 2)
    assert pred == pred
    assert pred == matching.Or(1, 2)
    assert matching.Or(1, 2, 3) != pred


def test_and():
    assert matching.And(matching.Ge(10), matching.Le(20)) == 10
    assert matching.And(matching.Ge(10), matching.Le(20)) == 15
    assert matching.And(matching.Ge(10), matching.Le(20)) == 20
    assert matching.And(matching.Ge(10), matching.Le(20)) != 21
    assert matching.And(matching.Ge(10), matching.Le(20)) != 9
    assert matching.And(matching.Ge(10), matching.Le(20)) != 'foo'

    pred = matching.And(1, 2)
    assert pred == pred
    assert pred == matching.And(1, 2)
    assert matching.And(1, 2, 3) != pred


def test_not():
    assert matching.Not(3) == 2
    assert matching.Not(3) != 3
    assert matching.Not(3) == 'foo'

    pred = matching.Not(3)
    assert pred == pred
    assert pred == matching.Not(3)
    assert pred != matching.Not(4)
