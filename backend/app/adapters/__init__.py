"""Data adapters.

Each adapter is a clean interface (Protocol-style base) with a Mock implementation.
Swapping to live data means writing a real impl with the same methods and selecting
it in `registry.py` — routers never change.
"""
from .registry import get_adapters, Adapters  # noqa: F401
