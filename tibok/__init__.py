"""TIBOK deployment tooling.

Imports are lazy so that `tibok.data_paths` -- which is pure stdlib and runs early in the
notebook, before the heavy stack is needed -- does not drag TensorFlow, NumPy and
scikit-learn in with it.
"""

__all__ = ["quantize_and_test", "quantize_int8", "compare_fp32_int8"]


def __getattr__(name):
    if name in __all__:
        from . import quantization
        return getattr(quantization, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
