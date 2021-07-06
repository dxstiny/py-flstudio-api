# name=API
# url=https://github.com/dxstiny/py-flstudio-api/
# author=dxstiny

import sys

print (sys.version)

import mixer
import ui
import midi
import plugins

from enum import Enum

from API_Finder import Finder
import API_logging

print()
print("finder.firstParamByName(query: str, plugin: number) -> e.g. (Gain, 2)")
print("finder.firstPluginByCallName(query: str) -> e.g. Lead 1, TwoKnob Piano, ...")
print("finder.firstPluginByPluginName(query: str) -> e.g. Serum, Patcher, ...")
print()

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

expectedMessageType = MessageType.none
cachedPlugin = ""
cachedParam = ""

finder = Finder()
logger = API_logging.GetLogger()
API_logging.SetLevel(API_logging.Level.info)

def OnMidiMsg(event):
	global cachedPlugin, cachedParam, expectedMessageType

	event.handled = True

	if event.midiId == midi.MIDI_NOTEON:
		if event.pmeFlags & midi.PME_System != 0:

			byte1, byte2, nibble3 = event.note, event.velocity, event.midiChan

			logger.trace(str(byte1) + " " + str(byte2) + " " + str(nibble3))

			if byte1 == 126: # start
				logger.debug("receive start bit for " + str(MessageType(byte2)))
				expectedMessageType = MessageType(byte2)
				if byte2 == 2:
					cachedPlugin = ""
				if byte2 == 3:
					cachedParam = ""

			elif byte1 == 127: # stop
				logger.debug("receive stop bit for " + str(MessageType(byte2)))
				expectedMessageType = -1

			elif expectedMessageType > MessageType.none:
				if expectedMessageType == MessageType.SetMixer:
					setMixer(byte1, byte2 / 100)

				elif expectedMessageType == MessageType.SetPluginParameter:
					setParam(byte1, nibble3, byte2 / 100)

				elif expectedMessageType == MessageType.CachePluginIndex:
					char = byte1 + byte2
					c = chr(char)
					cachedPlugin += c

				elif expectedMessageType == MessageType.CacheParameterIndex:
					char = byte1 + byte2
					c = chr(char)
					cachedParam += c

				elif expectedMessageType == MessageType.SetCachedPluginParameter:
					plugin = finder.firstPluginByCallName(cachedPlugin)
					if plugin == -1:
						logger.warning("no plugin w/ call name '" + cachedPlugin + "' found")
						return

					nibble3 = -1 if nibble3 == 15 else nibble3
					setParam(plugin, byte2, byte1 / 100, nibble3)

				elif expectedMessageType == MessageType.SetCachedPluginCachedParameter:
					logger.trace(str(byte1) + " " + str(byte2))
					byte2 = -1 if byte2 == 127 else byte2
					plugin = finder.firstPluginByCallName(cachedPlugin, byte2)
					if plugin == -1:
						logger.warning("no plugin w/ call name '" + str(cachedPlugin) + "' found")
						return

					param = finder.firstParamByName(cachedParam, plugin, byte2)
					if param == -1:
						logger.warning("no param w/ call name '" + str(cachedParam) + "' for plugin '" + str(cachedPlugin) + "' found")
						return

					setParam(plugin = plugin, param = param, value = (byte1 / 100), slot = byte2)
		else:
			event.handled = False
	else:
		event.handled = False

def setParam(plugin, param, value, slot = -1):
	logger.info("set param '"
		+ plugins.getParamName(param, plugin, slot)
		+ "' of plugin '"
		+ plugins.getPluginName(plugin, slot)
		+ "' to '" + str(value) + "'")
	plugins.setParamValue(value, param, plugin, slot)

def setMixer(track, volume):
	logger.info(str(track) + " " + str(volume))
	ui.showWindow(midi.widMixer)
	mixer.setTrackVolume(track, volume)
