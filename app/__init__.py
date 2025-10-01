"""Compatibility wrapper exposing the API package as a top-level ``app`` module."""
from importlib import import_module
from typing import Any, Iterable

_original = import_module("apps.api.app")

# Reuse the original package path so that submodules such as ``app.main``
# resolve to the FastAPI application implementation living under
# ``apps/api/app``.
__path__ = _original.__path__  # type: ignore[attr-defined]

# Export the public API from the original package. If ``__all__`` is defined
# we respect it; otherwise we fall back to every non-private attribute.
def _iter_public_attributes(module: Any) -> Iterable[str]:
    exported = getattr(module, "__all__", None)
    if exported is not None:
        return tuple(exported)
    return tuple(name for name in dir(module) if not name.startswith("_"))

__all__ = list(_iter_public_attributes(_original))

for name in __all__:
    globals()[name] = getattr(_original, name)

# Ensure commonly accessed callables are available even if they were not
# listed in ``__all__``.
for alias in ("Aplicacion", "CrearAplicacion"):
    if hasattr(_original, alias) and alias not in __all__:
        globals()[alias] = getattr(_original, alias)
        __all__.append(alias)
