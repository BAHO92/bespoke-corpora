from server.safety import is_safe_name


def test_safe_names():
    assert is_safe_name('my-corpus') is True
    assert is_safe_name('sillok_v2') is True
    assert is_safe_name('Corpus.2024') is True


def test_unsafe_names():
    assert is_safe_name('') is False
    assert is_safe_name('..') is False
    assert is_safe_name('../etc/passwd') is False
    assert is_safe_name('.hidden') is False
    assert is_safe_name('/absolute') is False
    assert is_safe_name('has space') is False
    assert is_safe_name('has/slash') is False
