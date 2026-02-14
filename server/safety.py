import re

_SAFE_NAME = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]*$')


def is_safe_name(name):
    if not name or not _SAFE_NAME.match(name):
        return False
    if '..' in name:
        return False
    return True
