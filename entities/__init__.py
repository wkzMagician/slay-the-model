"""Core entity types used by game."""

from .creature import Creature
# Enemy moved to enemies package - import from enemies package instead
# from enemies.base import Enemy  # Removed to avoid circular import

__all__ = ["Creature"]