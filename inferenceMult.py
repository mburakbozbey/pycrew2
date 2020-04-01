# Originally acquired from the repository by sentdex (https://github.com/Sentdex/pygta5)

import numpy as np
from grabscreen import grab_screen
import cv2
import time
from directkeys import PressKey,ReleaseKey, W, A, S, D
from getkeys import key_check
from collections import deque
import random
from statistics import mean
import numpy as np
from motion import motion_detection
from keras.models import model_from_json
import json
from keras.applications.densenet import preprocess_input


how_far_remove = 800
rs = (20,15)
log_len = 25

motion_req = 800
motion_log = deque(maxlen=log_len)

WIDTH = 224
HEIGHT = 224

choices = deque([], maxlen=5)
hl_hist = 250
choice_hist = deque([], maxlen=hl_hist)

inv_map = {0: 'a', 1: 'd', 2: 'nk', 3: 's', 4: 'sa', 5: 'sd', 6: 'w', 7: 'wa', 8: 'wd'}

t_time = 0.25

x1 = 273
x2 = 873
y1 = 638
y2 = 1238

map_labels = {  tuple([1,0,0,0]) : 6,
                tuple([0,1,0,0]) : 3,
                tuple([0,0,1,0]) : 0,
                tuple([0,0,0,1]) : 1,
                tuple([1,0,1,0]) : 7,
                tuple([1,0,0,1]) : 8,
                tuple([0,1,1,0]) : 4,
                tuple([0,1,0,1]) : 5,
                tuple([0,0,0,0]) : 3 ## noKey is mapped to brake
            }

def straight():
    PressKey(W)
    ReleaseKey(A)
    ReleaseKey(D)
    ReleaseKey(S)

def left():
    if random.randrange(0,3) == 1:
        PressKey(W)
    else:
        ReleaseKey(W)
    PressKey(A)
    ReleaseKey(S)
    ReleaseKey(D)
    #ReleaseKey(S)

def right():
    if random.randrange(0,3) == 1:
        PressKey(W)
    else:
        ReleaseKey(W)
    PressKey(D)
    ReleaseKey(A)
    ReleaseKey(S)
    
def reverse():
    PressKey(S)
    ReleaseKey(A)
    ReleaseKey(W)
    ReleaseKey(D)


def forward_left():
    PressKey(W)
    PressKey(A)
    ReleaseKey(D)
    ReleaseKey(S)
    
    
def forward_right():
    PressKey(W)
    PressKey(D)
    ReleaseKey(A)
    ReleaseKey(S)

    
def reverse_left():
    PressKey(S)
    PressKey(A)
    ReleaseKey(W)
    ReleaseKey(D)

    
def reverse_right():
    PressKey(S)
    PressKey(D)
    ReleaseKey(W)
    ReleaseKey(A)

## Reload weights & model structure:

with open(r'C:\Users\mbura\Desktop\crewModels\\logs\nvidiaMult\nvidiaMult.json','r') as f:
    model_json = json.load(f)

model = model_from_json(model_json)
model.load_weights(r'C:\Users\mbura\Desktop\pycrew2\logs\nvidiaMult\ep030-loss0.254-val_loss0.235.h5')
print('Model loaded.')



def main():
    last_time = time.time()
    for i in list(range(4))[::-1]:
        print(i+1)
        time.sleep(1)

    paused = False

    roi = grab_screen(region=(y1, x1, y2, x2))
    roi = cv2.resize(roi, (WIDTH, HEIGHT))
    prev = cv2.cvtColor(roi, cv2.COLOR_BGRA2RGB)

    t_minus = prev
    t_now = prev
    t_plus = prev

    while(True):
        
        if not paused:
            roi = grab_screen(region = (y1, x1, y2, x2))
            roi = cv2.resize(roi, (WIDTH, HEIGHT))
            roi = cv2.cvtColor(roi, cv2.COLOR_BGRA2RGB)

            last_time = time.time()
            roi = preprocess_input(roi)
            delta_count_last = motion_detection(np.asarray(t_minus, np.uint8), np.asarray(t_plus, np.uint8))

            t_minus = t_now
            t_now = t_plus
            t_plus = roi
            t_plus = cv2.blur(t_plus,(4,4))

            prediction = model.predict([roi.reshape(-1, roi.shape[0], roi.shape[1], roi.shape[2])])[0]
            prediction = np.rint(prediction)
            mode_choice = map_labels[tuple(prediction)]

            if mode_choice == 6:
                straight()
                choice_picked = 'straight'

            elif mode_choice == 3:
                reverse()
                choice_picked = 'reverse'

            elif mode_choice == 0:
                left()
                choice_picked = 'left'
            elif mode_choice == 1:
                right()
                choice_picked = 'right'
            elif mode_choice == 7:
                forward_left()
                choice_picked = 'forward+left'
            elif mode_choice == 8:
                forward_right()
                choice_picked = 'forward+right'
            elif mode_choice == 4:
                reverse_left()
                choice_picked = 'reverse+left'
            elif mode_choice == 5:
                reverse_right()
                choice_picked = 'reverse+right'

            motion_log.append(delta_count_last)
            motion_avg = round(mean(motion_log),3)
            print('loop took {} seconds. Motion: {}. Choice: {}'.format( round(time.time()-last_time, 3) , motion_avg, choice_picked))
            
            if motion_avg < motion_req and len(motion_log) >= log_len:
                print('WERE PROBABLY STUCK FFS, initiating some evasive maneuvers.')

                # 0 = reverse straight, turn left out
                # 1 = reverse straight, turn right out
                # 2 = reverse left, turn right out
                # 3 = reverse right, turn left out

                quick_choice = random.randrange(0,4)
                
                if quick_choice == 0:
                    reverse()
                    time.sleep(random.uniform(1,2))
                    forward_left()
                    time.sleep(random.uniform(1,2))

                elif quick_choice == 1:
                    reverse()
                    time.sleep(random.uniform(1,2))
                    forward_right()
                    time.sleep(random.uniform(1,2))

                elif quick_choice == 2:
                    reverse_left()
                    time.sleep(random.uniform(1,2))
                    forward_right()
                    time.sleep(random.uniform(1,2))

                elif quick_choice == 3:
                    reverse_right()
                    time.sleep(random.uniform(1,2))
                    forward_left()
                    time.sleep(random.uniform(1,2))

                for i in range(log_len-2):
                    del motion_log[0]
    
        keys = key_check()

        # p pauses game and can get annoying.
        if 'T' in keys:
            if paused:
                paused = False
                time.sleep(1)
            else:
                paused = True
                ReleaseKey(A)
                ReleaseKey(W)
                ReleaseKey(D)
                time.sleep(1)

main()       
