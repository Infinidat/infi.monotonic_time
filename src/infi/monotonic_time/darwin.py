import ctypes

SEC_IN_NSEC = 10**9

# Taken from /usr/include/mach/clock_types.h
SYSTEM_CLOCK = 0

_libc = None
_clock_get_time = None
_clock_serv = ctypes.c_void_p()


class c_mach_timespec(ctypes.Structure):
    # FIXME 32/64 - this is on a 64 bit machine.
    _fields_ = [("tv_sec", ctypes.c_uint32), ("tv_nsec", ctypes.c_uint32)]


def _init_library():
    global _libc, _clock_get_time, _clock_serv
    _libc = ctypes.CDLL("/usr/lib/libc.dylib")
    _libc.host_get_clock_service(_libc.mach_host_self(), SYSTEM_CLOCK, ctypes.byref(_clock_serv))
    _clock_get_time = _libc.clock_get_time


def _deinit_library():
    _libc.mach_post_deallocate(_libc.mach_task_self(), _clock_serv)


def monotonic_clock():
    if not _libc:
        _init_library()

    timespec = c_mach_timespec()
    _clock_get_time(_clock_serv, ctypes.byref(timespec))
    return timespec.tv_sec * SEC_IN_NSEC + timespec.tv_nsec


def time_to_monotonic(t):
    return int(t * SEC_IN_NSEC)


def time_from_monotonic(t):
    return float(t) / SEC_IN_NSEC
