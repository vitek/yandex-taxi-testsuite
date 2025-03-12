import pytest

from testsuite import matching


def test_any_float():
    assert matching.any_float == 1.0
    assert matching.any_float != 1
    assert matching.any_float != 'foo'


def test_any_integer():
    assert matching.any_integer == 1
    assert matching.any_integer != 1.0
    assert matching.any_integer != 'foo'


def test_any_numeric():
    assert matching.any_numeric == 1
    assert matching.any_numeric == 1.0
    assert matching.any_numeric != 'foo'


def test_positive_float():
    assert matching.positive_float != 0.0
    assert matching.positive_float == 1.0
    assert matching.positive_float != -1.0
    assert matching.positive_float != 'foo'


def test_positive_integer():
    assert matching.positive_integer != 0
    assert matching.positive_integer == 1
    assert matching.positive_integer != -1
    assert matching.positive_integer != 'foo'


def test_positive_numeric():
    assert matching.positive_numeric != 0.0
    assert matching.positive_numeric == 1.0
    assert matching.positive_numeric != -1.0
    assert matching.positive_numeric != 0
    assert matching.positive_numeric == 1
    assert matching.positive_numeric != -1
    assert matching.positive_numeric != 'foo'


def test_negative_float():
    assert matching.negative_float != 0.0
    assert matching.negative_float != 1.0
    assert matching.negative_float == -1.0
    assert matching.negative_float != 'foo'


def test_negative_integer():
    assert matching.negative_integer != 0
    assert matching.negative_integer != 1
    assert matching.negative_integer == -1
    assert matching.negative_integer != 'foo'


def test_negative_numeric():
    assert matching.negative_numeric != 0.0
    assert matching.negative_numeric != 1.0
    assert matching.negative_numeric == -1.0
    assert matching.negative_numeric != 0
    assert matching.negative_numeric != 1
    assert matching.negative_numeric == -1
    assert matching.negative_numeric != 'foo'


def test_non_negative_float():
    assert matching.non_negative_float == 0.0
    assert matching.non_negative_float == 1.0
    assert matching.non_negative_float != -1.0
    assert matching.non_negative_float != 'foo'


def test_non_negative_integer():
    assert matching.non_negative_integer == 0
    assert matching.non_negative_integer == 1
    assert matching.non_negative_integer != -1
    assert matching.non_negative_integer != 'foo'


def test_non_negative_numeric():
    assert matching.non_negative_numeric == 0.0
    assert matching.non_negative_numeric == 1.0
    assert matching.non_negative_numeric != -1.0
    assert matching.non_negative_numeric == 0
    assert matching.non_negative_numeric == 1
    assert matching.non_negative_numeric != -1
    assert matching.non_negative_numeric != 'foo'


def test_gt():
    assert matching.Gt(0) != 0
    assert matching.Gt(0) == 1
    assert matching.Gt(0) != -1
    assert matching.Gt(0) != 'foo'


def test_ge():
    assert matching.Ge(0) == 0
    assert matching.Ge(0) == 1
    assert matching.Ge(0) != -1
    assert matching.Ge(0) != 'foo'


def test_lt():
    assert matching.Lt(0) != 0
    assert matching.Lt(0) != 1
    assert matching.Lt(0) == -1
    assert matching.Lt(0) != 'foo'


def test_le():
    assert matching.Le(0) == 0
    assert matching.Le(0) != 1
    assert matching.Le(0) == -1
    assert matching.Le(0) != 'foo'


@pytest.mark.parametrize(
    'instance',
    [
        matching.any_float,
        matching.any_integer,
        matching.any_numeric,
        matching.positive_float,
        matching.positive_integer,
        matching.positive_numeric,
        matching.negative_float,
        matching.negative_integer,
        matching.negative_numeric,
        matching.non_negative_float,
        matching.non_negative_integer,
        matching.non_negative_numeric,
    ],
)
def test_instances(instance):
    assert instance == instance


def test_equals():
    pred = matching.Ge(0)
    assert pred == pred
    assert pred == matching.Ge(0)
    assert pred != matching.Ge(1)
