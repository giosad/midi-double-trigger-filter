# [midi-double-trigger-filter](https://github.com/giosad/midi-double-trigger-filter)
Processes MIDI events from a controller to filter note-on events caused by unintended double triggering.

Confirmed to work with MPD218 in Win10 and macOs.

## Screenshot
[![midi-note-double-trigger-filter.png](https://s33.postimg.cc/p3emgfmnz/midi-note-double-trigger-filter.png)](https://postimg.cc/image/yny93bbzv/)
## Requirements
For MIDI filtering you need :
- Virtual midi device
    - for Windows you can use:
        - [LoopBe1](http://www.nerds.de/en/loopbe1.html)
        - [loopMIDI](http://www.tobias-erichsen.de/software/loopmidi.html)
    - for macOS
        - Refer to [google](http://www.google.com/search?q=macos+virtual+midi+port) for instructions.
- python3 and the following packages:
```sh
$ pip install python-rtmidi appdirs
```

## How to use
- Create a virtual MIDI device (one time only). 
 - Run the MIDI filter, set input to a physical MIDI controller device and output as virtual MIDI device. Press Start.
 - Start the app you want to use with the MIDI controller, configure its input to be the virtual MIDI device.

