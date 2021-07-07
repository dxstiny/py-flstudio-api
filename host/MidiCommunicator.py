# url=https://github.com/dxstiny/py-flstudio-api/
# author=dxstiny

from typing import Union

import pygame.midi

class MidiCommunicator():
    def __init__(self):
        pygame.midi.init()
        self._player = pygame.midi.Output(self._tryFindOutputDevice())

    def _tryFindOutputDevice(self):
        devices = self._getOutputDevices()
        for device in devices:
            if "loopMIDI" in device["name"]:
                print("device " + device["name"] + " found")
                return device["id"]
        print("no device found, defaulting to " + devices[0]["name"])
        return devices[0]["id"]

    def _getOutputDevices(self):
        l = []
        device_count = pygame.midi.get_count()
        for d in range(device_count):
            device = pygame.midi.get_device_info(d)
            device_name = device[1].decode()
            device_type = device[2]
            if device_type == 0:
                l.append({"name": device_name, "id": d})
        return l

    def _normaliseSlot(self, slot, max = 127):
        return max if slot == -1 else 0

    def _normalise(self, value, max = 100):
        return max if value > max else value

    def setPluginParameter(self,
            plugin: Union[str, int],
            value: int,
            parameter: Union[str, int],
            slot = -1):

        # try casting
        if isinstance(plugin, str) and str.isdigit(plugin):
            plugin = int(plugin)
        if isinstance(parameter, str) and str.isdigit(parameter):
            parameter = int(parameter)

        # cache if necessary
        if isinstance(plugin, str):
            self._cachePluginIndex(plugin)
        else: # is int
            pass
        if isinstance(parameter, str):
            self._cacheParameterIndex(parameter)
        else: # is int
            pass

        # set
        if isinstance(plugin, str) and isinstance(parameter, str) and slot == -1:
            self._setCachedPluginCachedParameter(value, slot)
        elif isinstance(plugin, str) and isinstance(parameter, int) and slot == -1:
            self._setCachedPluginParameter(value, parameter, slot)
        elif isinstance(plugin, int) and isinstance(parameter, int) and slot == -1:
            self._setPluginParameter(plugin, value, parameter)
        elif isinstance(plugin, int) and isinstance(parameter, str):
            self._setEffectParameter(plugin, value, parameter, slot)
        else:
            x = "MidiCommunicator.setPluginParameter - no matching function found!"
            print(x)
            return x

        return "success"

    def setmixer(self, mixer, volume):
        volume = self._normalise(volume)
        self._startMessage(0)
        self._sendBytes(mixer, volume)
        self._stopMessage(0)

    def _setEffectParameter(self, plugin: int, value: int, parameter: str, slot: int):
        self._cachePluginIndex(plugin)
        self._cacheParameterIndex(parameter)
        self._setCachedPluginCachedParameter(value, slot)

    def _setPluginParameter(self, plugin: int, value: int, parameter: int):
        self._startMessage(1)
        self._sendBytes(plugin, self._normalise(value), parameter)
        self._stopMessage(1)

    def _cachePluginIndex(self, string: Union[str, int]):
        self._startMessage(2)
        self._sendString(string)
        self._stopMessage(2)

    def _cacheParameterIndex(self, string: str):
        self._startMessage(3)
        self._sendString(string)
        self._stopMessage(3)

    def _setCachedPluginParameter(self, value: int, parameter: int, slot: int):
        self._startMessage(4)
        self._sendBytes(self._normalise(value), self._normalise(parameter, max = 127), self._normaliseSlot(slot, max = 15))
        self._stopMessage(4)

    def _setCachedPluginCachedParameter(self, value: int, slot: int):
        self._startMessage(5)
        self._sendBytes(self._normalise(value), self._normaliseSlot(slot))
        self._stopMessage(5)

    def _stopMessage(self, function: int):
        self._sendBytes(127, function)

    def _startMessage(self, function: int, additional = 0):
        self._sendBytes(126, function, additional)

    def _sendString(self, string: Union[str, int]):
        if isinstance(string, int):
            char = string
            byte1 = 127 if char > 127 else char
            byte2 = char - 127 if char > 127 else 0
            self._sendBytes(byte1, byte2)
            return

        for cha in string:
            char = ord(cha)
            byte1 = 127 if char > 127 else char
            byte2 = char - 127 if char > 127 else 0
            self._sendBytes(byte1, byte2)

    def _sendBytes(self, byte1: int, byte2: int, nibble3 = 0):
        # byte1: note, byte2: velocity, byte3: channel
        self._player.note_on(byte1, byte2, nibble3)
        self._player.note_off(byte1, 0, nibble3)
