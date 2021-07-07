# url=https://github.com/dxstiny/py-flstudio-api/
# author=dxstiny

from enum import Enum

import midi

import API_logging

logger = API_logging.GetLogger()

class MessageType(Enum):
    def __gt__(self, b):
        return self.value > b.value

    none = -1
    SetMixer = 0
    SetPluginParameter = 1
    CachePluginIndex = 2
    CacheParameterIndex = 3
    SetCachedPluginParameter = 4
    SetCachedPluginCachedParameter = 5

class MidiCommunicatorReceiver():
    def __init__(self, OnSetMixer = None,
            OnSetPluginParameter = None,
            OnSetCachedPluginParameter = None,
            OnSetCachedPluginCachedParameter = None):

        self._logger = API_logging.GetLogger("MidiReceiver")
        self._cachedPlugin = ""
        self._cachedParameter = ""
        self._expectedMessageType = MessageType.none
        self.OnSetMixer = OnSetMixer
        self.OnSetPluginParameter = OnSetPluginParameter
        self.OnSetCachedPluginParameter = OnSetCachedPluginParameter
        self.OnSetCachedPluginCachedParameter = OnSetCachedPluginCachedParameter

    # basic receiver

    def OnMidiMsg(self, event):
        event.handled = False
        if not event.midiId == midi.MIDI_NOTEON:
            return
        if not event.pmeFlags & midi.PME_System != 0:
            return
        event.handled = True

        byte1, byte2, nibble3 = event.note, event.velocity, event.midiChan

        self._logger.trace("1: " + str(byte1) + ", 2: " + str(byte2) + ", 3: " + str(nibble3))

        if byte1 == 126: # start
            self._onStartMessage(byte1, byte2, nibble3)
            return

        if byte1 == 127: # stop
            self._onStopMessage(byte1, byte2, nibble3)
            return

        if self._expectedMessageType == MessageType.none:
            return

        if self._expectedMessageType == MessageType.SetMixer and self.OnSetMixer:
            self.OnSetMixer(byte1, byte2 / 100) # insert, volume
            return

        if self._expectedMessageType == MessageType.SetPluginParameter and self.OnSetPluginParameter:
            self.OnSetPluginParameter(byte1, nibble3, byte2 / 100) # plugin, param, value
            return

        if self._expectedMessageType == MessageType.SetCachedPluginParameter and self.OnSetCachedPluginParameter:
            self.OnSetCachedPluginParameter(self._cachedPlugin, byte2, byte1 / 100, -1 if nibble3 == 15 else nibble3)
            return

        if self._expectedMessageType == MessageType.SetCachedPluginCachedParameter and self.OnSetCachedPluginCachedParameter:
            self.OnSetCachedPluginCachedParameter(self._cachedPlugin, self._cachedParameter, byte1 / 100, byte2 if not byte2 == 127 else -1)
            return

        if self._expectedMessageType == MessageType.CachePluginIndex:
            self._onCachePlugin(byte1, byte2, nibble3)
            return

        if self._expectedMessageType == MessageType.CacheParameterIndex:
            self._onCacheParameter(byte1, byte2, nibble3)
            return

    # basic protocol

    def _onStartMessage(self, byte1, byte2, nibble3):
        self._logger.debug("receive start bit for " + str(MessageType(byte2)))
        self._expectedMessageType = MessageType(byte2)
        if self._expectedMessageType == MessageType.CachePluginIndex:
            self._cachedPlugin = ""
        if self._expectedMessageType == MessageType.CacheParameterIndex:
            self._cachedParameter = ""

    def _onStopMessage(self, byte1, byte2, nibble3):
        logger.debug("receive stop bit for " + str(MessageType(byte2)))
        self._expectedMessageType = -1

    # advanced protocol

    def _parseString(self, byte1, byte2, nibble3):
        char = byte1 + byte2
        c = chr(char)
        return c

    def _onCachePlugin(self, byte1, byte2, nibble3):
        self._cachedPlugin += self._parseString(byte1, byte2, nibble3)

    def _onCacheParameter(self, byte1, byte2, nibble3):
        self._cachedParameter += self._parseString(byte1, byte2, nibble3)