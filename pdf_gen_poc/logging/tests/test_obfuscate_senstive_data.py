from pdf_gen_poc.logging import obfuscate_sensitive_args


def test_obfuscate_sensitive_args() -> None:
    assert obfuscate_sensitive_args(sensitive_data=['x'], arguments=[{'a': 1}, {'x': 2}]) == [{'a': 1}, {'x': '***'}]


def test_obfuscate_sensitive_kwargs() -> None:
    assert obfuscate_sensitive_args(sensitive_data=['x'], arguments={'a': 1, 'x': 2}) == {'a': 1, 'x': '***'}


def test_obfuscate_sensitive_kwargs_nested_data() -> None:
    assert obfuscate_sensitive_args(sensitive_data=['x'], arguments={'a': 1, 'b': {'x': 2}}) == {
        'a': 1,
        'b': {'x': '***'},
    }


def test_obfuscate_sensitive_kwargs_no_data() -> None:
    assert obfuscate_sensitive_args([], {'a': 5, 'b': 'six'}) == {'a': 5, 'b': 'six'}


def test_obfuscate_sensitive_kwargs_is_not_in_kwargs() -> None:
    assert obfuscate_sensitive_args(['c'], {'a': 5, 'b': 'six'}) == {'a': 5, 'b': 'six'}
