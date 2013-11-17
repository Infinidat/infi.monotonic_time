import platform

__all__ = ['is_supported', 'monotonic_time']

def not_implemented_error():
    raise NotImplementedError("monotonic clock support is not implemented for this platform")

system = platform.system()
if system == "Linux":
    from .linux import monotonic_clock, time_to_monotonic, time_from_monotonic
elif system == "Darwin":
    from .darwin import monotonic_clock, time_to_monotonic, time_from_monotonic
else:
    monotonic_clock = not_implemented_error
    time_to_monotonic = not_implemented_error
    time_from_monotonic = not_implemented_error


def monotonic_time():
    """
    :raises NotImplementedError: if system does not support monotonic clock
    :raises OSError: in case of failure
    """
    return time_from_monotonic(monotonic_clock())


def is_supported():
    try:
        monotonic_time()
        return True
    except NotImplementedError:
        return False
