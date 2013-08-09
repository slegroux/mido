"""
Experimental wrapper for python-rtmidi:
https://pypi.python.org/pypi/python-rtmidi/

This module only supports a limited number of MIDI message types,
as listed below.

I tested sending all messags types in these directions:

    rtmidi -> rtmidi
    rtmidi -> portmidi
    portmidi -> rtmidi

These were received in all cases:

    note_off
    note_on
    polytouch
    control_change
    program_change
    aftertouch
    pitchwheel
    songpos
    song_select

In addition, sysex was received in "rtmidi -> portmidi", and only there.

Since PortMidi is able to send and receive all message types, it seems
that the limitation is in RtMidi or python-rtmidi. This will require
some further investigation.
"""
from __future__ import absolute_import
import time
import mido
import rtmidi
from ..ports import BaseInput, BaseOutput

def get_devices():
    devices = []

    input_names = set(rtmidi.MidiIn().get_ports())
    output_names = set(rtmidi.MidiOut().get_ports())

    for name in sorted(input_names | output_names):
        devices.append({
                'name' : name,
                'is_input' : name in input_names,
                'is_output' : name in output_names,
                })

    return devices

class PortCommon(object):
    def _open(self, **kwargs):

        opening_input = hasattr(self, 'receive')

        if opening_input:
            self._rt = rtmidi.MidiIn()
            # print(self._rt.ignore_types(['note_on']))
        else:
            self._rt = rtmidi.MidiOut()

        ports = self._rt.get_ports()

        if self.name is None:
            # Todo: this could fail if list is empty.
            # In RtMidi, the default port is the first port.
            try:
                self.name = ports[0]
            except IndexError:
                raise IOError('no ports available')

        try:
            port_id = ports.index(self.name)
        except ValueError:
            raise IOError('unknown port {!r}'.format(name))

        self._rt.open_port(port_id)

    def _close(self):
        self._rt.close_port()

class Input(PortCommon, BaseInput):
    # Todo: sysex messages do not arrive here.
    def _pending(self):
        while 1:
            message = self._rt.get_message()
            if message is None:
                break
            else:
                self._parser.feed(message[0])
            
class Output(PortCommon, BaseOutput):
    def _send(self, message):
        self.rt._send_message(message.bytes())
