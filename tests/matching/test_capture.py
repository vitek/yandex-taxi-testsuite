import pytest

from testsuite import matching


def test_capture():
    capture_foo = matching.Capture()
    pattern = {'foo': capture_foo}
    assert pattern == {'foo': 'bar'}
    assert capture_foo.value == 'bar'
    assert capture_foo.values_list == ['bar']


def test_capture_multiple():
    capture_foo = matching.Capture()
    pattern = {'foo': capture_foo}
    assert pattern == {'foo': 'bar'}
    assert pattern == {'foo': 'baz'}
    assert capture_foo.value == 'bar'
    assert capture_foo.values_list == ['bar', 'baz']


def test_capture_failure():
    capture_foo = matching.Capture(matching.any_string)
    pattern = {'foo': capture_foo}
    assert pattern != {'foo': 1}
    with pytest.raises(matching.NoValueCapturedError):
        capture_foo.value
    assert capture_foo.values_list == []


def test_instance():
    cap = matching.Capture(123)
    assert cap == cap

    assert matching.Capture(123) == matching.Capture(123)
    assert matching.Capture(123) != matching.Capture(321)
