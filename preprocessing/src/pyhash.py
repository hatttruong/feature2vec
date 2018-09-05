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
        int_i = int(ord(str[i]))
        print('str=%s, int=%s' % (str[i], int_i))
        h = h ^ int_i
        print('h ^ = %s' % int(h))
        h = h * 16777619
        print('h * = %s' % int(h))
    return h
