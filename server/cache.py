from pathlib import Path

_store = {}


def get_or_load(key, paths, loader):
    if isinstance(paths, (str, Path)):
        paths = {str(paths): Path(paths)}
    elif isinstance(paths, list):
        paths = {str(p): Path(p) for p in paths}

    mtimes = {}
    for label, p in paths.items():
        try:
            mtimes[label] = p.stat().st_mtime
        except OSError:
            mtimes[label] = 0

    cached = _store.get(key)
    if cached and cached['mtimes'] == mtimes:
        return cached['data']

    data = loader(paths)
    _store[key] = {'mtimes': mtimes, 'data': data}
    return data


def invalidate(key=None):
    if key:
        _store.pop(key, None)
    else:
        _store.clear()
