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


class MIDIFilter:
    def __init__(self):
        self._iport = None
        self._oport = None
        CHANNEL_COUNT = 16
        NOTES_COUNT = 128
        self._notes_on_times = [[0]*NOTES_COUNT]*CHANNEL_COUNT
        self.enabled = True
        self.min_delay = 0.06 # in seconds
        self.min_velocity = 40
        self.enabled2 = False
        self.min_delay2 = 0.05  # in seconds
        self.min_velocity2 = 80
        self.notes_on_events_passed = 0
        self.notes_on_events_skipped = 0
        self.stats_updated_cb = None
        self._is_running = False


    def is_running(self):
        return self._is_running

    def stats_updated(self):
        if self.stats_updated_cb:
            self.stats_updated_cb()


    def list_iports(self):
        return self._scan_ports(rtmidi.MidiIn())


    def list_oports(self):
        return self._scan_ports(rtmidi.MidiOut())


    def _scan_ports(self, midi_obj):
        return [midi_obj.get_port_name(i) for i in range(midi_obj.get_port_count())]


    def _port_index_by_name(self, midi_obj, portname):
        port_names = self._scan_ports(midi_obj)
        filtered = [index for (index, name) in enumerate(port_names) if portname == name]
        return filtered[0] if filtered else -1


    def start(self, iportname, oportname):
        self.stop()
        self._oport = rtmidi.MidiOut()
        self._iport = rtmidi.MidiIn()


        def handle_in(msg, useData):
            msg, time_from_prev_note = msg
            ctime = time.time()
            skip = False
            note_on = False
            delta = 0
            NOTE_ON = 0x90
            COMMAND_MASK = 0xF0
            CHANNEL_MASK = 0x0F
            note_on = (msg[0] & COMMAND_MASK) == NOTE_ON

            if note_on:
                channel = msg[0] & CHANNEL_MASK
                note = msg[1]
                velocity = msg[2]
                delta = ctime - self._notes_on_times[channel][note]

                if self.enabled:
                    too_fast = delta < self.min_delay
                    too_weak = velocity < self.min_velocity
                    skip = skip or (too_fast and too_weak)
					
                if self.enabled2:
                    too_fast2 = delta < self.min_delay2
                    too_weak2 = velocity < self.min_velocity2
                    skip = skip or (too_fast2 and too_weak2)

            if not skip:
                if note_on:
                    self._notes_on_times[channel][note] = ctime
                    self.notes_on_events_passed += 1
                    self.stats_updated()
                self._oport.send_message(msg)
            else:
                self.notes_on_events_skipped += 1
                self.stats_updated()
                xprint('Skipping note_on of note {}, delta {:.3f}, velocity={}'.format(msg[1], delta, msg[2]))

        self._oport.open_port(self._port_index_by_name(self._oport, oportname))
        if not self._oport.is_port_open():
            xprint('Output MIDI device is not found')
            return

        self._iport.set_callback(handle_in)
        self._iport.open_port(self._port_index_by_name(self._iport, iportname))
        if not self._iport.is_port_open():
            xprint('Input MIDI device is not found')
            return

        xprint('Ports open')
        self._is_running = True


    def stop(self):
        self._is_running = False
        if self._iport:
            self._iport.set_callback(None)
            self._iport.close_port()
            self._iport = None

        if self._oport:
            self._oport.close_port()
            self._oport = None

        xprint('MIDI ports closed')
