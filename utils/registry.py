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


def get_registered(category: str, name: str):
    """Get registered item(s) from a category."""
    if category not in _REGISTRY:
        return None

    if name:
        return _REGISTRY[category].get(name)
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