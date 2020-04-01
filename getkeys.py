# Citation: Box Of Hats (https://github.com/Box-Of-Hats )
# Originally acquired from the repository by sentdex (https://github.com/Sentdex/pygta5)

import win32api as wapi
import time

keyList = ["\b"]
for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ 123456789,.'£$/\\":
    keyList.append(char)

def key_check():
    keys = []
    for key in keyList:
        if wapi.GetAsyncKeyState(ord(key)):
            keys.append(key)
    return keys
 
