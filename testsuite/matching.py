import collections.abc
import operator
import re
import typing

import dateutil.parser


class BaseError(Exception):
    pass


class NoValueCapturedError(BaseError):
    pass


def _collect_base_types(conditions):
    types = set()
    for cond in conditions:
        if hasattr(cond, '__testsuite_type__'):
            types.add(cond.__testsuite_type__)
    return tuple(types)


class Any:
    """Matches any value."""

    # Used by assert_repr compare
    __testsuite_type__ = object

    def __repr__(self):
        return '<Any>'

    def __eq__(self, other):
        return True


class AnyString:
    """Matches any string."""

    __testsuite_type__ = str

    def __repr__(self):
        return '<AnyString>'

    def __eq__(self, other):
        if isinstance(other, str) or self is other:
            return True
        if isinstance(other, AnyString):
            return True
        return False


class RegexString:
    """Match string with regular expression.

    .. code-block:: python

       assert response.json() == {
          'order_id': matching.RegexString('^[0-9a-f]*$'),
          ...
       }
    """

    __testsuite_type__ = str

    def __init__(self, pattern):
        self._pattern = re.compile(pattern)

    def __repr__(self):
        return f'<{self.__class__.__name__} pattern={self._pattern!r}>'

    def __eq__(self, other):
        if isinstance(other, str):
            return self._pattern.match(other) is not None
        if other is self:
            return True
        if isinstance(other, RegexString):
            return self._pattern == other._pattern
        return False


class UuidString(RegexString):
    """Matches lower-case hexadecimal uuid string."""

    def __init__(self):
        super().__init__('^[0-9a-f]{32}$')


class ObjectIdString(RegexString):
    """Matches lower-case hexadecimal objectid string."""

    def __init__(self):
        super().__init__('^[0-9a-f]{24}$')


class DatetimeString(AnyString):
    """Matches datetime string in any format."""

    def __repr__(self):
        return '<DatetimeString>'

    def __eq__(self, other):
        if not super().__eq__(other):
            return False

        try:
            dateutil.parser.parse(other)
            return True
        except ValueError:
            return False


class IsInstance:
    """Match value by its type.

    Use this class when you only need to check value type.

    .. code-block:: python

       assert response.json() == {
          # order_id must be a string
          'order_id': matching.IsInstance(str),
          # int or float is acceptable here
          'weight': matching.IsInstance(int, float),
          ...
       }
    """

    def __init__(self, *types):
        testsuite_types = []
        for type in types:
            if isinstance(types, (list, tuple)):
                testsuite_types.extend(types)
            else:
                testsuite_types.append(type)
        self.__testsuite_type__ = tuple(testsuite_types)

    def __repr__(self):
        type_names = [t.__name__ for t in self.__testsuite_type__]
        return f'<IsInstance {", ".join(type_names)}>'

    def __eq__(self, other):
        if isinstance(other, self.__testsuite_type__):
            return True
        if self is other:
            return True
        if not isinstance(other, IsInstance):
            return False
        return self.__testsuite_type__ == other.__testsuite_type__


class And:
    """Checks that all conditions are True.

    .. code-block:: python

       # match integer is in range [10, 100)
       assert num == matching.And(matching.Ge(10), matching.Lt(100))
    """

    def __init__(self, *conditions):
        self.__testsuite_type__ = _collect_base_types(conditions)
        self._conditions = conditions

    def __repr__(self):
        conditions = [repr(cond) for cond in self._conditions]
        return f'<All {" ".join(conditions)}>'

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, And):
            return self._conditions == other._conditions
        for condition in self._conditions:
            if condition != other:
                return False
        return True


class Or:
    """Checks that some of conditions is True.

    .. code-block:: python

       # match integers abs(num) >= 10
       assert num == matching.Or(matching.Ge(10), matching.Le(-10))
    """

    def __init__(self, *conditions):
        self.__testsuite_type__ = _collect_base_types(conditions)
        self._conditions = conditions

    def __repr__(self):
        conditions = [repr(cond) for cond in self._conditions]
        return f'<Or {" ".join(conditions)}>'

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, Or):
            return self._conditions == other._conditions
        for condition in self._conditions:
            if condition == other:
                return True
        return False


class Not:
    """Condition inversion.

    Example:

    .. code-block:: python

       # check value is not 1
       assert value == matching.Not(1)
    """

    def __init__(self, condition):
        self._condition = condition

    def __repr__(self):
        return f'<Not {self._condition!r}>'

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, Not):
            return self._condition == other._condition
        return self._condition != other


class Comparator:
    op: typing.Callable[[typing.Any, typing.Any], bool] = operator.eq

    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return f'<{self.op.__name__} {self._value}>'

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, Comparator):
            return self.op is other.op and self._value == other._value
        try:
            return self.op(other, self._value)
        except TypeError:
            return False


class Gt(Comparator):
    """Value is greater than.

    Example:

    .. code-block:: python

       # Value must be > 10
       assert value == matching.Gt(10)
    """

    op = operator.gt


class Ge(Comparator):
    """Value is greater or equal.

    Example:

    .. code-block:: python

       # Value must be >= 10
       assert value == matching.Ge(10)
    """

    op = operator.ge


class Lt(Comparator):
    """Value is less than.

    Example:

    .. code-block:: python

       # Value must be < 10
       assert value == matching.Lt(10)
    """

    op = operator.lt


class Le(Comparator):
    """Value is less or equal.

    Example:

    .. code-block:: python

       # Value must be <= 10
       assert value == matching.Le(10)
    """

    op = operator.le


class PartialDict(collections.abc.Mapping):
    """Partial dictionary comparison.

    Sometimes you only need to check dictionary subset ignoring all
    other keys. :py:class:`PartialDict` is there for this purpose.

    `PartialDict` is wrapper around regular `dict()` when instantiated
    all arguments are passed as is to internal dict object.

    Example:

    .. code-block:: python

       assert {'foo': 1, 'bar': 2} == matching.PartialDict({
           # Only check for foo >= 1 ignoring other keys
           'foo': matching.Ge(1),
       })
    """

    __testsuite_type__ = dict

    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)

    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return self._dict.get(item, any_value)

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return f'<PartialDict {self._dict!r}>'

    def __eq__(self, other):
        if not isinstance(other, collections.abc.Mapping):
            return False

        for key in self:
            if other.get(key) != self.get(key):
                return False

        return True

    def __testsuite_len__(self):
        return Ge(len(self))

    def __testsuite_resolve_value__(self, other):
        result = other.copy()
        result.update(self._dict)
        return result


class UnorderedList:
    __testsuite_type__ = list

    def __init__(self, sequence, key):
        self._value = sorted(sequence, key=key)
        self._key = key

    def __repr__(self):
        return f'<UnorderedList: {self._value}>'

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, list):
            return sorted(other, key=self._key) == self._value
        if not isinstance(other, UnorderedList):
            return False
        return self._value == other._value and self._key == other._key

    # def __testsuite_resolve_value__(self, other):
    #     # TODO: restore original order
    #     return sorted(other, key=self._key)


class AnyList:
    """Value is a list.

    Example:

    .. code-block:: python

       assert ['foo', 'bar']  == matching.any_dict
    """

    __testsuite_type__ = list

    def __testsuite_len__(self):
        return non_negative_integer

    def __repr__(self):
        return '<AnyList>'

    def __eq__(self, other):
        return isinstance(other, list) or isinstance(other, AnyList)


class ListOf(AnyList):
    """Value is a list of values.

    Example:

    .. code-block:: python

       assert ['foo', 'bar']  == matching.ListOf(matching.any_string)
       assert [1, 2]  != matching.ListOf(matching.any_string)
    """

    def __init__(self, item):
        self._item = item

    def __repr__(self):
        return f'<ListOf item={self._item}>'

    def __eq__(self, other):
        if isinstance(other, list):
            for item in other:
                if self._item != item:
                    return False
            return True
        if self is other:
            return True
        if not isinstance(other, ListOf):
            return False
        return self._item == other._item

    def __testsuite_resolve_value__(self, other):
        return [self._item] * len(other)


class AnyDict:
    """Value is a dictionary.

    Example:

    .. code-block:: python

       assert {'foo': 'bar'} == matching.any_dict
    """

    __testsuite_type__ = dict

    def __testsuite_len__(self):
        return non_negative_integer

    def __repr__(self):
        return '<AnyDict>'

    def __eq__(self, other):
        return isinstance(other, dict) or isinstance(other, AnyDict)


class DictOf(AnyDict):
    """Value is a dictionary of (key, value) pairs.

    Example:

    .. code-block:: python

       pred = matching.DictOf(key=matching.any_string, value=matching.any_string)
       assert pred == {'foo': 'bar'}
       assert pred != {'foo': 1}
       assert pred != {1: 'bar'}
    """

    def __init__(self, key=Any(), value=Any()):
        self._key = key
        self._value = value

    def __repr__(self):
        return f'<DictOf key={self._key} value={self._value}>'

    def __eq__(self, other):
        if isinstance(other, dict):
            for key, value in other.items():
                if self._key != key:
                    return False
                if self._value != value:
                    return False
            return True

        if self is other:
            return True
        if not isinstance(other, DictOf):
            return False
        return self._key == other._key and self._value == other._value

    def __testsuite_resolve_value__(self, other):
        result = {}
        for key, value in other.items():
            if key != self._key:
                # raise key does not match error
                result[self._key] = self._value
            else:
                result[key] = self._value
        return other.items(), result


class Capture:
    """Capture matched value(s).

    Example:

    .. code-block:: python

       capture_foo = matching.Capture()
       pattern = {'foo': capture_foo}
       assert pattern == {'foo': 'bar'}
       assert capture_foo.value == 'bar'
       assert capture_foo.values_list == ['bar']
    """

    def __init__(self, value=Any()):
        self.__testsuite_type__ = _collect_base_types((value,))
        self._value = value
        self._captured = []

    @property
    def value(self):
        if self._captured:
            return self._captured[0]
        raise NoValueCapturedError(f'No value captured for value {self._value}')

    @property
    def values_list(self):
        return self._captured

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, Capture):
            return other._value == self._value
        if self._value != other:
            return False
        self._captured.append(other)
        return True


def unordered_list(sequence, *, key=None):
    """Unordered list comparison.

    You may want to compare lists without respect to order. For instance,
    when your service is serializing std::unordered_map to array.

    `unordered_list` can help you with that. It sorts both array before
    comparison.

    :param sequence: Initial sequence
    :param key: Sorting key function

    Example:

    .. code-block:: python

       assert [3, 2, 1] == matching.unordered_list([1, 2, 3])
    """
    return UnorderedList(sequence, key)


any = any_value = Any()
any_float = IsInstance(float)
any_integer = IsInstance(int)
any_numeric = IsInstance(int, float)
positive_float = And(any_float, Gt(0))
positive_integer = And(any_integer, Gt(0))
positive_numeric = And(any_numeric, Gt(0))
negative_float = And(any_float, Lt(0))
negative_integer = And(any_integer, Lt(0))
negative_numeric = And(any_numeric, Lt(0))
non_negative_float = And(any_float, Ge(0))
non_negative_integer = And(any_integer, Ge(0))
non_negative_numeric = And(any_numeric, Ge(0))
any_string = AnyString()
datetime_string = DatetimeString()
objectid_string = ObjectIdString()
uuid_string = UuidString()

any_dict = AnyDict()
any_list = AnyList()
