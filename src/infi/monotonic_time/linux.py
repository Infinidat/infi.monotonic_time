# Linux-specific implementation (specifically >= 2.6.21), although the clock_getxxx are POSIX.
# See more with man clock_gettime and man 7 time

from ctypes import CDLL, Structure, c_int64, c_int32, c_long, byref, get_errno
from sysconfig import get_config_var

__all__ = ['monotonic_clock', 'time_to_monotonic', 'time_from_monotonic']

CLOCK_REALTIME = 0
CLOCK_MONOTONIC = 1
CLOCK_MONOTONIC_RAW = 4

_rtlib = None
_time_t = None
_timespec_t = None

SEC_IN_NSEC = 10**9


def _init_library():
    global _rtlib, _time_t, _timespec_t

    _time_t = c_int64 if get_config_var("SIZEOF_TIME_T") == 8 else c_int32

    class timespec_t(Structure):
        _fields_ = [("tv_sec", _time_t), ("tv_nsec", c_long)]

    _timespec_t = timespec_t

    try:
        _rtlib = CDLL("librt.so")
    except OSError:
        raise NotImplementedError("system doesn't support high resolution timers (librt.so not found)")

    # First we need to see that the clock we want is supported.
    # See man 7 time: High-Resolution Timers
    if _rtlib.clock_getres(CLOCK_MONOTONIC_RAW, 0) != 0:
        raise NotImplementedError("system doesn't support high resolution timers or monotonic clock")


def monotonic_clock():
    if not _rtlib:
        _init_library()

    timespec = _timespec_t()
    if _rtlib.clock_gettime(CLOCK_MONOTONIC_RAW, byref(timespec)) != 0:
        raise OSError(get_errno(), "clock_gettime failed")

    return timespec.tv_nsec + (timespec.tv_sec * SEC_IN_NSEC)


def time_to_monotonic(time):
    return int(time * SEC_IN_NSEC)


def time_from_monotonic(clock):
    return clock / float(SEC_IN_NSEC)
