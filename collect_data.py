import cv2
import os
import time
# import matplotlib.pyplot as plt
from grabscreen import grab_screen
from getkeys import key_check

# Define keys/classes

w  = [1,0,0,0,0,0,0,0,0]
s  = [0,1,0,0,0,0,0,0,0]
a  = [0,0,1,0,0,0,0,0,0]
d  = [0,0,0,1,0,0,0,0,0]
wa = [0,0,0,0,1,0,0,0,0]
wd = [0,0,0,0,0,1,0,0,0]
sa = [0,0,0,0,0,0,1,0,0]
sd = [0,0,0,0,0,0,0,1,0]
nk = [0,0,0,0,0,0,0,0,1]

## ROI coordinates

x1 = 273
x2 = 873
y1 = 638
y2 = 1238

def keys_to_output(keys):
    '''
    Convert keys to a ...multi-hot... array
     0  1  2  3  4   5   6   7    8
    [W, S, A, D, WA, WD, SA, SD, NOKEY] boolean values.
    '''
    output = "empty"

    if 'W' in keys and 'A' in keys:
        output = "wa"
    elif 'W' in keys and 'D' in keys:
        output = "wd"
    elif 'S' in keys and 'A' in keys:
        output = "sa"
    elif 'S' in keys and 'D' in keys:
        output = "sd"
    elif 'W' in keys:
        output = "w"
    elif 'S' in keys:
        output = "s"
    elif 'A' in keys:
        output = "a"
    elif 'D' in keys:
        output = "d"
    else:
        output = "nk"
    return output


# Average FPS = 56

def main():
    # session log
    # first sess = 0 - 9.970
    # second sess = 10.000 - 86.833
    # third sess = 87.000 -
    idx = 87000
    p = False

    for i in list(range(10))[::-1]:
        print(i + 1)
        time.sleep(1)

    print('Capturing starts.')
    # ave = 0
    # t1 = time.time()
    while(True):
        if not p:

            roi = grab_screen(region = (y1, x1, y2, x2))
            keys = key_check()
            roi = cv2.cvtColor(roi, cv2.COLOR_BGRA2BGR)
            roi = cv2.resize(roi, (224, 224))

            # print(roi)
            # plt.imshow(cv2.cvtColor(roi, cv2.COLOR_BGRA2RGB))
            # plt.show()

            class_name = keys_to_output(keys)
            path = 'C:/Users/mbura/Desktop/pycrewDataset/train/'+ class_name + '/{}.jpg'.format(idx)
            cv2.imwrite(path, roi)
            # t2 = time.time()
            # ave = t2-t1
            idx += 1
            # print("FPS: {}".format(idx/ave))
            time.sleep(.1)


        keys = key_check()

        if 'T' in keys:
            if p:
                p = False
                print('Continue capturing.')
                time.sleep(1)
            else:
                print('Capturing is paused. ')
                p = True
                time.sleep(1)


main()