"""
llama_cpp.py — Transparent proxy to the real llama-cpp-python package.

This file exists in the backend folder so the app can boot even without llama-cpp-python.
When the real package IS installed, this module replaces itself in sys.modules so that
all downstream imports (e.g. `from llama_cpp import Llama`) resolve to the real library.
"""

import os
import sys

# Remove THIS file's directory from sys.path before the real import so Python
# doesn't resolve "llama_cpp" back to this file (which would cause recursion).
_this_dir = os.path.dirname(os.path.abspath(__file__))
_clean_path = [p for p in sys.path if os.path.abspath(p).lower() != _this_dir.lower()]

try:
    import importlib

    # Temporarily swap sys.path so the real package is found in site-packages
    _orig_path = sys.path[:]
    sys.path = _clean_path

    # Also remove the cached entry for this dummy module before importing the real one
    sys.modules.pop("llama_cpp", None)

    _real = importlib.import_module("llama_cpp")

    # Compatibility layer for older llama.dll versions that do not support llama_get_memory
    if hasattr(_real, "llama_cpp") and hasattr(_real.llama_cpp, "_lib"):
        lib = _real.llama_cpp._lib
        if not hasattr(lib, "llama_get_memory"):
            import ctypes

            # Bind the older KV cache manager functions
            if hasattr(lib, "llama_kv_cache_clear"):
                lib.llama_kv_cache_clear.argtypes = [_real.llama_context_p_ctypes]
                lib.llama_kv_cache_clear.restype = None
            if hasattr(lib, "llama_kv_cache_seq_rm"):
                lib.llama_kv_cache_seq_rm.argtypes = [
                    _real.llama_context_p_ctypes,
                    _real.llama_seq_id,
                    _real.llama_pos,
                    _real.llama_pos,
                ]
                lib.llama_kv_cache_seq_rm.restype = ctypes.c_bool
            if hasattr(lib, "llama_kv_cache_seq_cp"):
                lib.llama_kv_cache_seq_cp.argtypes = [
                    _real.llama_context_p_ctypes,
                    _real.llama_seq_id,
                    _real.llama_seq_id,
                    _real.llama_pos,
                    _real.llama_pos,
                ]
                lib.llama_kv_cache_seq_cp.restype = None
            if hasattr(lib, "llama_kv_cache_seq_keep"):
                lib.llama_kv_cache_seq_keep.argtypes = [
                    _real.llama_context_p_ctypes,
                    _real.llama_seq_id,
                ]
                lib.llama_kv_cache_seq_keep.restype = None
            if hasattr(lib, "llama_kv_cache_seq_add"):
                lib.llama_kv_cache_seq_add.argtypes = [
                    _real.llama_context_p_ctypes,
                    _real.llama_seq_id,
                    _real.llama_pos,
                    _real.llama_pos,
                    _real.llama_pos,
                ]
                lib.llama_kv_cache_seq_add.restype = None

            # Patch llama_get_memory and memory functions
            _real.llama_get_memory = lambda ctx: ctx
            _real.llama_memory_clear = lambda memory, v: (
                lib.llama_kv_cache_clear(memory) if hasattr(lib, "llama_kv_cache_clear") else None
            )
            _real.llama_memory_seq_rm = lambda memory, seq_id, p0, p1: (
                lib.llama_kv_cache_seq_rm(memory, seq_id, p0, p1)
                if hasattr(lib, "llama_kv_cache_seq_rm")
                else False
            )
            _real.llama_memory_seq_cp = lambda memory, seq_id_src, seq_id_dst, p0, p1: (
                lib.llama_kv_cache_seq_cp(memory, seq_id_src, seq_id_dst, p0, p1)
                if hasattr(lib, "llama_kv_cache_seq_cp")
                else None
            )
            _real.llama_memory_seq_keep = lambda memory, seq_id: (
                lib.llama_kv_cache_seq_keep(memory, seq_id)
                if hasattr(lib, "llama_kv_cache_seq_keep")
                else None
            )
            _real.llama_memory_seq_add = lambda memory, seq_id, p0, p1, shift: (
                lib.llama_kv_cache_seq_add(memory, seq_id, p0, p1, shift)
                if hasattr(lib, "llama_kv_cache_seq_add")
                else None
            )

            # Expose in inner namespaces
            _real.llama_cpp.llama_get_memory = _real.llama_get_memory
            _real.llama_cpp.llama_memory_clear = _real.llama_memory_clear
            _real.llama_cpp.llama_memory_seq_rm = _real.llama_memory_seq_rm
            _real.llama_cpp.llama_memory_seq_cp = _real.llama_memory_seq_cp
            _real.llama_cpp.llama_memory_seq_keep = _real.llama_memory_seq_keep
            _real.llama_cpp.llama_memory_seq_add = _real.llama_memory_seq_add

    # Restore the path
    sys.path = _orig_path

    # Replace *this* module in sys.modules with the real package so that
    # any subsequent `from llama_cpp import Llama` resolves correctly.
    sys.modules[__name__] = _real

    # Make all real symbols available at module-import time as well
    globals().update({k: v for k, v in _real.__dict__.items() if not k.startswith("__")})

    _REAL_LOADED = True

except Exception as _load_err:
    sys.path = sys.path if "_orig_path" not in dir() else _orig_path  # type: ignore[name-defined]
    _REAL_LOADED = False
    _real = None  # type: ignore[assignment]

    print(
        f"[WARNING] llama-cpp-python not available ({_load_err}). "
        "AI chat will be disabled. "
        "To fix: uv pip install llama-cpp-python "
        "--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu"
    )

    # Fallback stub — raises informative error when actually instantiated
    class Llama:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "llama-cpp-python is not installed.\n"
                "Run: uv pip install llama-cpp-python "
                "--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu\n"
                "Then restart the backend server."
            )
