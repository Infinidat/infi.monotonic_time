import ctypes
import os

SEC_IN_NSEC = 10**9

# Taken from /usr/include/mach/clock_types.h
SYSTEM_CLOCK = 0

class ModuleGlobals(object):
    # a container for variables that would normally be simple global variables,
    # but we want to have one set per process to avoid sharing the variables.
    # regular globals and thread-local-storage does not work - once the
    # parent process sets them, child processes may get its values.
    # https://stackoverflow.com/a/660468
    # https://stackoverflow.com/a/7285797
    _libc = None
    _clock_serv = ctypes.c_void_p()


globals_by_pid = dict()


class c_mach_timespec(ctypes.Structure):
    # FIXME 32/64 - this is on a 64 bit machine.
    _fields_ = [("tv_sec", ctypes.c_uint32), ("tv_nsec", ctypes.c_uint32)]


def _init_library():
    global_vars = ModuleGlobals()
    global_vars._libc = ctypes.CDLL("/usr/lib/libc.dylib")
    global_vars._libc.host_get_clock_service(
        global_vars._libc.mach_host_self(),
        SYSTEM_CLOCK,
        ctypes.byref(global_vars._clock_serv)
    )
    globals_by_pid[os.getpid()] = global_vars
    return global_vars


def _deinit_library():
    global_vars = globals_by_pid[os.getpid()]
    global_vars._libc.mach_post_deallocate(
        global_vars._libc.mach_task_self(),
        global_vars._clock_serv
    )


def monotonic_clock():
    if os.getpid() not in globals_by_pid:
        _init_library()
    global_vars = globals_by_pid[os.getpid()]

    timespec = c_mach_timespec()
    global_vars._libc.clock_get_time(
        global_vars._clock_serv,
        ctypes.byref(timespec)
    )
    return timespec.tv_sec * SEC_IN_NSEC + timespec.tv_nsec


def time_to_monotonic(t):
    return int(t * SEC_IN_NSEC)


def time_from_monotonic(t):
    return float(t) / SEC_IN_NSEC
