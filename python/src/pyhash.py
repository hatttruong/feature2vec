import ctypes


def hash(str):
    """Do the same in C++

    Args:
        str (TYPE): Description

    Returns:
        TYPE: Description
    """
    h = 2166136261
    for i in range(len(str)):
        h = h ^ ctypes.c_uint32(int8_t(str[i]))
        h = h * 16777619
    return h
