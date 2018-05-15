# Copyright (c) 2018 Gennadi Iosad.
# All Rights Reserved.
# You may use, distribute and modify this code under the
# terms of the MIT license.
#
# You should have received a copy of the MIT license with
# this file.

# Requirements
# pip install python-rtmidi
# pip install mido

import mido
from mido.frozen import freeze_message, thaw_message
import sys
import time

def xprint(*args, **kwargs):
    t = time.time()
    timestamp = time.strftime('%H:%M:%S', time.localtime(t)) + '.{:03}'.format(int(t * 1000) % 1000)
    print(timestamp, *args, **kwargs)

inputs = mido.get_input_names()
controllerName = [x for x in inputs if '218' in x][0]
outputs = mido.get_output_names()
virtualDeviceName = [x for x in outputs if 'LoopBe' in x][0]

if controllerName == None:
    print('Target MIDI controller is not found')
    print('Available inputs', inputs)
    sys.exit(1)

xprint('Target MIDI controller is found:', controllerName)

if virtualDeviceName == None:
    print('Target MIDI virtual output is not found')
    print('Available outputs', outputs)
    sys.exit(1)
    
xprint('Target virtual MIDI output is found:', virtualDeviceName)

notes_on_times = [0]*128
notes_off_times = [0]*128
min_delay = 0.06  # in seconds

min_velocity = 40

min_delay2 = 0.05  # in seconds
min_velocity2 = 80

with mido.open_input(controllerName, autoreset=True) as iport, (
     mido.open_output(virtualDeviceName, autoreset=True)) as oport:

#    for msg in map(freeze_message, iport):
    for msg in iport:
        ctime = time.time()
        skip = False
        delta = 0
        if msg.type == 'note_on':
            delta = ctime - notes_on_times[msg.note]
            too_fast = delta < min_delay
            too_weak = msg.velocity < min_velocity
            too_fast2 = delta < min_delay2
            too_weak2 = msg.velocity < min_velocity2
            
            #too_weak = True
            #too_weak2 = True
            if (too_fast and too_weak) or (too_fast2 and too_weak2):
                skip = True
            else:
                xprint('delta', delta)
                notes_on_times[msg.note] = ctime
                
            #if too_fast and not too_weak:
            #    xprint('FISHY', delta, msg)

            
        if msg.type == 'note_off':
            notes_off_times[msg.note] = ctime
        
        if not skip:
            oport.send(msg)
            
        else:
            #old_note = msg.dict()['note']
            #msg = msg.copy(note=old_note-1)
            #oport.send(msg)
            xprint('Skipping {:.3f}'.format(delta), msg)
             
            

