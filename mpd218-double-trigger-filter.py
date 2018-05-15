# Copyright (c) 2018 Gennadi Iosad.
# All Rights Reserved.
# You may use, distribute and modify this code under the
# terms of the MIT license.
#
# You should have received a copy of the MIT license with
# this file.

# Requirements
# pip install python-rtmidi

import rtmidi
import sys
import time

def xprint(*args, **kwargs):
    t = time.time()
    timestamp = time.strftime('%H:%M:%S', time.localtime(t)) + '.{:03}'.format(int(t * 1000) % 1000)
    print(timestamp, *args, **kwargs)

def scan_ports(midi_obj, name_substring):
    ports = [(i, midi_obj.get_port_name(i)) for i in range(midi_obj.get_port_count())]
    filtered_ports = [(index, port_name) for (index, port_name) in ports if name_substring in port_name]
    return filtered_ports[0] if filtered_ports else (-1, None)
    
#    for msg in map(freeze_message, iport):
def handle_in(msg, useData):
    msg, time_from_prev_note = msg
    ctime = time.time()
    skip = False
    delta = 0
    NOTE_ON = 0x90
    COMMAND_MASK = 0xF0
    if (msg[0] & COMMAND_MASK) == NOTE_ON:
        channel = msg[0] & 0x0F
        note = msg[1]
        velocity = msg[2]
        delta = ctime - notes_on_times[channel][note]
        too_fast = delta < min_delay
        too_weak = velocity < min_velocity
        too_fast2 = delta < min_delay2
        too_weak2 = velocity < min_velocity2
        
        #too_weak = True
        #too_weak2 = True
        if (too_fast and too_weak) or (too_fast2 and too_weak2):
            skip = True
        else:
            #xprint('delta', delta)
            notes_on_times[channel][note] = ctime            
        
    if not skip:
        midiout.send_message(msg)
    else:
        xprint('Skipping {:.3f}'.format(delta), msg)
         
        
CHANNEL_COUNT = 16
NOTES_COUNT = 128
notes_on_times = [[0]*NOTES_COUNT]*CHANNEL_COUNT
midiin = None
midiout = None
min_delay = 0.06 # in seconds
min_velocity = 40

min_delay2 = 0.05  # in seconds
min_velocity2 = 80

def start():
    global midiin, midiout
    
    midiin = rtmidi.MidiIn()
    input_port_index, input_port_name = scan_ports(midiin, '218')

    if input_port_index < 0:
        xprint('Target MIDI controller is not found')
        sys.exit(1)

    xprint('Target MIDI controller is found:', input_port_name)

    midiout = rtmidi.MidiOut()
    output_port_index, output_port_name = scan_ports(midiout, 'LoopBe')
    if output_port_index < 0:
        xprint('Target MIDI virtual output is not found')
        sys.exit(1)
        
    xprint('Target virtual MIDI output is found:', output_port_name)
    midiin.set_callback(handle_in)
    midiin.open_port(input_port_index)
    midiout.open_port(output_port_index)

def stop():
    global midiin, midiout
    if midiin:
        midiin.set_callback(None)
        midiin.close_port()
    if midiout:
        midiout.close_port()
    xprint('MIDI ports closed')
    

import tkinter as tk
import tkinter.ttk as ttk
top = tk.Tk()
topFrame = tk.LabelFrame(top, text='12')
topFrame.pack()
startB = ttk.Button(topFrame, text = "Start", command=start)
startB.pack(side=tk.LEFT,padx=20, pady=20)
stopB = ttk.Button(topFrame, text = "Stop", command=stop)
stopB.pack(side=tk.RIGHT)
top.update()
top.minsize(top.winfo_width(), top.winfo_height())
top.mainloop()
