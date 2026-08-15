"""
Unified registry for all game components.
"""

from typing import Any

_REGISTRY = {}


def register(category: str):
    """
    Unified decorator to register any component type.

    Usage:
        @register("room")
        class MyRoom(Room):
            pass

        @register("event")
        def my_event(event):
            pass

        @register("action")
        class MyAction(Action):
            pass
    """
    def decorator(obj: Any):
        if category not in _REGISTRY:
            _REGISTRY[category] = {}

        # Get name from class __name__ or try to evaluate idstr property
        if hasattr(obj, "__name__"):
            name = obj.__name__
        else:
            # For functions, try idstr if it exists
            name = getattr(obj, "idstr", None)
            if name and callable(name):
                name = name()

        if name:
            _REGISTRY[category][name] = obj

        return obj
    return decorator


def _normalize_key(name: str) -> str:
    """Normalize an identifier for tolerant matching.

    Converts CamelCase to snake_case and lowercases, e.g. 'FungiBeast' ->
    'fungi_beast'.  Existing snake_case names are returned unchanged.
    """
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0 and (name[i - 1].islower() or name[i - 1].isdigit()):
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


def get_registered(category: str, name: str):
    """Get registered item(s) from a category.

    Lookup is tolerant: keys stored as class names (e.g. 'FungiBeast') can
    be queried in snake_case (e.g. 'fungi_beast').
    """
    if category not in _REGISTRY:
        return None

    if not name:
        return None

    registry = _REGISTRY[category]
    if name in registry:
        return registry[name]

    needle = _normalize_key(name)
    for key, value in registry.items():
        if _normalize_key(key) == needle:
            return value
    return None


def list_registered(category: str):
    """List all registered items in a category."""
    if category not in _REGISTRY:
        return []
    return list(_REGISTRY[category].keys())

# 获得实例的一个新拷贝
def get_registered_instance(category: str, name: str, **kwargs):
    """Get a new instance of a registered item from a category."""
    cls = get_registered(category, name)
    if cls:
        return cls(**kwargs)
    return None