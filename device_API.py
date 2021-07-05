# name=API
# url=https://forum.image-line.com/viewtopic.php?p=1483607#p1483607

# This import section is loading the back-end code required to execute the script. You may not need all modules that are available for all scripts.

import sys

print (sys.version)

import mixer
import ui
import midi
import plugins
import channels

#The next two variables are constants defined up here so you don't need tp go hunting in the script to find them later. Good habit. 
#You can name these as you like, so long as you use them in the script below as written ...

import time

print()
print("findParam(query: str, plugin: number) -> e.g. (Gain, 2)")
print("findPluginNameIndex(query: str) -> e.g. Lead 1, TwoKnob Piano, ...")
print("findPluginIndex(query: str) -> e.g. Serum, Patcher, ...")
print()

expectedMessageType = -1
cachedPlugin = ""
cachedParam = ""

class TSimple():

	def OnMidiMsg(self, event):
		global cachedPlugin, cachedParam, expectedMessageType

		event.handled = True

		if event.midiId == midi.MIDI_NOTEON:
			if (event.pmeFlags & midi.PME_System != 0):

				byte1, byte2, nibble3 = event.note, event.velocity, event.midiChan

				#print(byte1, byte2, nibble3)

				if byte1 == 126: # start
					print("receive start bit for " + str(byte2))
					expectedMessageType = byte2
					if byte2 == 2:
						cachedPlugin = ""
					if byte2 == 3:
						cachedParam = ""

				elif byte1 == 127: # stop
					print("receive stop bit for " + str(byte2))
					expectedMessageType = -1

				elif expectedMessageType >= 0:
					if expectedMessageType == 0:
						setMixer(byte1, byte2 / 100)
					elif expectedMessageType == 1:
						setParam(byte1, nibble3, byte2 / 100)
					elif expectedMessageType == 2:
						char = byte1 + byte2
						c = chr(char)
						cachedPlugin += c
					elif expectedMessageType == 3:
						char = byte1 + byte2
						c = chr(char)
						cachedParam += c
					elif expectedMessageType == 4:
						plugin = findPluginNameIndex(cachedPlugin)
						print(cachedPlugin, plugin)
						setParam(plugin, byte2, byte1 / 100)
					elif expectedMessageType == 5:
						print(byte1, byte2)
						byte2 = -1 if byte2 == 127 else byte2
						plugin = findPluginNameIndex(cachedPlugin, byte2)
						param = findParam(cachedParam, plugin, byte2)
						print(cachedPlugin, plugin, param, byte2)
						setParam(plugin, param, byte1 / 100, byte2)
			else:
				event.handled = False
		else:
			event.handled = False

Simple = TSimple()

def setParam(plugin, param, value, slot):
	print("set param '" + plugins.getParamName(param, plugin, slot) + "' of plugin '" + plugins.getPluginName(plugin, slot) + "' to '" + str(value) + "'")
	plugins.setParamValue(value, param, plugin, slot)

def setMixer(track, volume):
	print(track, volume)
	ui.showWindow(midi.widMixer)
	mixer.setTrackVolume(track, volume)

def OnMidiMsg(event):
	Simple.OnMidiMsg(event)

def rand_val(x):
    random=int(time.time()*1000)
    random %= x
    return random

def findParam(query, plugin, slot):
	count = plugins.getParamCount(plugin, slot)
	for i in range(count):
		if query.lower() in plugins.getParamName(i, plugin, slot).lower():
			print(plugins.getParamName(i, plugin, slot))
			return i
	return -1

def findPluginNameIndex(query, slot):
	if slot is not -1:
		return ord(query)

	count = channels.channelCount(1)

	for i in range(count):
		print(channels.getChannelName(i))
		if query.lower() in channels.getChannelName(i).lower():
			try:
				print(plugins.getPluginName(i) + " named " + channels.getChannelName(i))
				return i
			except:
				pass
	return -1

def findPluginIndex(query):
	count = channels.channelCount(1)

	for i in range(count):
		try:
			if query.lower() in plugins.getPluginName(i).lower():
				#print(plugins.getPluginName(i))
				return i
		except TypeError:
			pass
	return -1
