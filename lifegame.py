"""
Lifegame

Use bit to represent status may be more efficient but, nah.
"""
import os
from time import sleep

import numpy as np

shape = (40, 40)
rlocs = [(x, y) for x in (-1, 0, 1) for y in (-1, 0, 1) if x or y]
frame = np.random.randint(0, 2, (shape))
cache = np.array(frame)


def fprint(frame):
    for i in frame:
        print(''.join('⬜' if j == 0 else '⬛' for j in i))


def fgen():
    loc = np.array([0, 0], dtype=np.int8)
    for index, status in np.ndenumerate(cache):
        count = 0
        for rloc in rlocs:
            if rloc == (0, 0):
                continue
            loc[0], loc[1] = index[0] + rloc[0], index[1] + rloc[1]
            if loc[0] == cache.shape[0]:
                loc[0] = 0
            if loc[1] == cache.shape[1]:
                loc[1] = 0
            if cache[loc[0], loc[1]] == 1:
                count += 1
        if status == 0 and count == 3:
            frame[index[0], index[1]] = 1
        elif status == 1 and count not in {2, 3}:
            frame[index[0], index[1]] = 0


while True:
    fprint(frame)
    fgen()
    cache[:] = frame
    sleep(0.01)
    os.system('clear')
