#!/usr/bin/python3

from ctypes import c_ulong

def hash_data(data,size):
    ret = [c_ulong(0x6b901122fd987193),
           c_ulong(0xf61e2562c040b340),
           c_ulong(0xd62f105d02441453),
           c_ulong(0x21e1cde6c33707d6)]
    i = 0
    while(i < size):
        try:
            v = data[i]
        except Exception as e:
            print(e)
            print(" i : {x} , data :  {y}".format(x = i,y = data))
        j = 1
        while(j < 64):
            mask = c_ulong((ret[j & 0x3].value>>j) & 3)
            ret[mask.value].value = (ret[mask.value]).value + (~(v) << j)
            ret[mask.value].value = ret[mask.value].value - (i + 1) * j * (v + 1)
            ret[mask.value].value = ret[mask.value].value +ret[(ret[mask.value].value >> j) & mask.value].value
            j = j + 5
        ret[0].value = ret[0].value ^ ret[1].value
        ret[1].value = ret[1].value ^ ret[2].value
        ret[2].value = ret[2].value ^ ret[3].value
        ret[3].value = ret[3].value ^ ret[0].value
        i = i + 1
    return ret


