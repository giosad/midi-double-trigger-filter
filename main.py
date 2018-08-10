#!/usr/bin/env python3

# Copyright (c) 2018 Gennadi Iosad.
# All Rights Reserved.
# You may use, distribute and modify this code under the
# terms of the MIT license.
#
# You should have received a copy of the MIT license with
# this file.

import tkinter as tk
import tkinter.ttk as ttk
import appdirs
import configparser
import os

from midi_filter import *


class DoubleTriggerFilterView:
    def __init__(self, root, midi_filter, config):
        self.root = root
        self.midi_filter = midi_filter
        self.config = config

        # vars
        self.iportname = tk.StringVar(window)
        self.oportname = tk.StringVar(window)
        self.status = tk.StringVar(window)
        self.autostart = tk.IntVar(window)

        self.filter1_enabled = tk.IntVar(window)
        self.min_delay = tk.StringVar(window)
        self.min_velocity = tk.StringVar(window)

        self.notes_on_events_passed = tk.IntVar(window)
        self.notes_on_events_skipped = tk.IntVar(window)

        self.setup_devices_frame()
        self.setup_filter_frame()
        self.setup_stats_frame()
        self.setup_operations_frame()

        self.rescan()
        self.load_config()


        def stats_updated_cb():
            self.notes_on_events_passed.set(self.midi_filter.notes_on_events_passed)
            self.notes_on_events_skipped.set(self.midi_filter.notes_on_events_skipped)
        self.midi_filter.stats_updated_cb = stats_updated_cb
        stats_updated_cb()


        def set_min_velocity(*args):
            try:
                v = float(self.min_velocity.get())
            except ValueError:
                v = 0
            self.midi_filter.min_velocity = v
        self.min_velocity.trace('w', set_min_velocity)


        def set_min_delay(*args):
            try:
                v = float(self.min_delay.get())
            except ValueError:
                v = 0
            self.midi_filter.min_delay = v
        self.min_delay.trace('w', set_min_delay)


        def filter1_enabled(*args):
            self.midi_filter.enabled = self.filter1_enabled.get()
        self.filter1_enabled.trace('w', filter1_enabled)

        if self.autostart.get():
            self.start()


    def load_config(self):
        try:
            self.iportname.set(self.config.get('general', 'in', fallback='[NONE]'))
            self.oportname.set(self.config.get('general', 'out', fallback='[NONE]'))
            self.autostart.set(int(self.config.getboolean('general', 'autostart', fallback=0)))
            self.min_delay.set(self.config.getfloat('filter1', 'min_delay', fallback=self.midi_filter.min_delay))
            self.min_velocity.set(int(self.config.getfloat('filter1', 'min_velocity', fallback=self.midi_filter.min_velocity)))
            self.filter1_enabled.set(int(self.config.getboolean('filter1', 'enabled', fallback=1)))
        except ValueError:
            pass


    def update_config(self):
        self.config.set('general', 'in', self.iportname.get())
        self.config.set('general', 'out', self.oportname.get())
        self.config.set('general', 'autostart', str(self.autostart.get()))
        self.config.set('filter1', 'min_delay', str(self.min_delay.get()))
        self.config.set('filter1', 'min_velocity', str(self.min_velocity.get()))
        self.config.set('filter1', 'enabled', str(self.filter1_enabled.get()))


    def rescan(self):
        iports = self.midi_filter.list_iports()
        self.update_option_menu(self.iport_menu, iports if iports else ['[NONE]'], self.iportname)
        oports = self.midi_filter.list_oports()
        self.update_option_menu(self.oport_menu, oports if oports else ['[NONE]'], self.oportname)


    def update_option_menu(self, menu, choices, tkvar):
        menu.delete(0, 'end')
        for string in choices:
            menu.add_command(label=string, command=lambda value=string: tkvar.set(value))
        if tkvar.get() not in choices:
            tkvar.set(choices[0])


    def start(self):
        self.midi_filter.start(self.iportname.get(), self.oportname.get())
        self.update_status()


    def stop(self):
        self.midi_filter.stop()
        self.update_status()


    def toggle_start_stop(self):
        if self.midi_filter.is_running():
            self.stop()
        else:
            self.start()

    def update_status(self):
        if self.midi_filter.is_running():
            self.status.set('Stop')
        else:
            self.status.set('Start')


    def setup_devices_frame(self):
        choices = ['[NONE]']
        self.oportname.set(choices[0])
        self.iportname.set(choices[0])

        devices_frame = tk.LabelFrame(self.root, text='Devices', padx=20, pady=20)
        devices_frame.pack(fill=tk.X, padx=20, pady=10)

        io_frame = tk.Frame(devices_frame)
        io_frame.pack(fill=tk.X, pady=10)
        io_frame.grid_columnconfigure(0, weight=0)
        io_frame.grid_columnconfigure(1, weight=1)

        input_midi_devices_label = ttk.Label(io_frame, text='Input:')
        input_midi_devices_label.grid(row=0, sticky=tk.E)

        input_midi_devices = ttk.OptionMenu(io_frame, self.iportname, *choices)
        input_midi_devices.grid(row=0, column=1, sticky=tk.W)
        self.iport_menu = input_midi_devices['menu']

        output_midi_devices_label = ttk.Label(io_frame, text='Output:')
        output_midi_devices_label.grid(row=1, sticky=tk.E)

        output_midi_devices = ttk.OptionMenu(io_frame, self.oportname, *choices)
        output_midi_devices.grid(row=1, column=1, sticky=tk.W)
        self.oport_menu = output_midi_devices['menu']

        rescan_btn = ttk.Button(devices_frame, text = "Rescan", command = lambda:self.rescan())
        rescan_btn.pack(ipady=5)


    def setup_filter_frame(self):
        filter_frame = tk.LabelFrame(self.root, text='Filter', padx=20, pady=20)
        filter_frame.pack(fill=tk.X, padx=20, pady=10)

        output_midi_devices_label = ttk.Label(filter_frame, text='Minimum time delta (secs)')
        output_midi_devices_label.grid(row=0, sticky=tk.E)

        min_delta_entry = tk.Spinbox(filter_frame, from_=0.01, to=0.1, increment=0.01, textvariable=self.min_delay)
        min_delta_entry.grid(row=0, column=1, padx=10)

        spacer = tk.Frame(filter_frame)
        spacer.grid(row=1, column=0, ipady=5, ipadx=10)

        min_velocity_devices_label = ttk.Label(filter_frame, text='Minimum velocity (1-127)')
        min_velocity_devices_label.grid(row=2, sticky=tk.E)

        min_velocity_entry = tk.Spinbox(filter_frame, from_=1, to=127, textvariable=self.min_velocity)
        min_velocity_entry.grid(row=2, column=1, padx=10)

        enabled_chkbtn = ttk.Checkbutton(filter_frame, text='Enabled', variable = self.filter1_enabled)
        enabled_chkbtn.grid(column=2, row=0, rowspan=3, padx=20, sticky=tk.E)


    def setup_stats_frame(self):
        stats_frame = tk.LabelFrame(self.root, text='MIDI note-on events stats', padx=20, pady=20)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)

        notes_events = ttk.Label(stats_frame, text='Passed')
        notes_events.grid(row=0, column=0, sticky=tk.E)

        notes_events_count = ttk.Entry(stats_frame, textvariable=self.notes_on_events_passed)
        notes_events_count.grid(row=0, column=1, sticky=tk.E, padx=10, pady=5)

        skipped = ttk.Label(stats_frame, text='Skipped')
        skipped.grid(row=0, column=2, sticky=tk.E)

        skipped_count = ttk.Entry(stats_frame, textvariable=self.notes_on_events_skipped)
        skipped_count.grid(row=0, column=3, sticky=tk.E, padx=10, pady=5)


    def setup_operations_frame(self):
        operation_frame = tk.Frame(window)
        operation_frame.pack()

        start_btn = ttk.Button(operation_frame, textvariable = self.status, command = lambda:self.toggle_start_stop())
        start_btn.pack(pady=5, ipady=2)

        autostart_chkbtn = ttk.Checkbutton(window, text='Autostart', variable = self.autostart)
        autostart_chkbtn.pack(pady=10)



# Config.
config_dir = appdirs.user_config_dir('midi-note-double-trigger-filter', '')
config_path = os.path.join(config_dir, 'midi-note-double-trigger-filter.cfg')
debug_log('Config at:', config_path)
config = configparser.ConfigParser()
config.read(config_path)
if 'general' not in config: config.add_section('general')
if 'filter1' not in config: config.add_section('filter1')

# Model and view
window = tk.Tk()
window.title("MIDI Note Double Trigger Filter")

midi_filter = MIDIFilter()
view = DoubleTriggerFilterView(window, midi_filter, config)

window.update()
window.minsize(window.winfo_width(), window.winfo_height())
window.mainloop()

midi_filter.stats_updated_cb = None
view.update_config()

# Save config to file
if not os.path.exists(config_dir):
    os.makedirs(config_dir)
config.write(open(config_path, 'w'))

debug_log('EXIT')
