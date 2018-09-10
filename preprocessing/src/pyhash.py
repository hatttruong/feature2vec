"""Summary
"""
import ctypes
import numpy as np


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
        # print('str=%s, int=%s' % (str[i], int_i))
        h = np.uint32(h ^ int_i)
        # print('h ^ = %s' % h)
        h = np.uint32(h * 16777619)
        # print('h * = %s' % h)

    int_h = int(h)
    assert int_h == h, "converting uint32(%s) to int(%s) is incorrect" % (
        h, int_h)
    return int_h

if __name__ == '__main__':
    hash('Runs Vtach')