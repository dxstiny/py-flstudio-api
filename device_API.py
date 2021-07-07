# name=API
# url=https://github.com/dxstiny/py-flstudio-api/
# author=dxstiny

import sys

import mixer
import ui
import midi
import plugins

from API_Finder import Finder
from MidiCommunicatorReceiver import MidiCommunicatorReceiver
import API_logging

print (sys.version)
print()
print("finder.firstParamByName(query: str, plugin: number) -> e.g. (Gain, 2)")
print("finder.firstPluginByCallName(query: str) -> e.g. Lead 1, TwoKnob Piano, ...")
print("finder.firstPluginByPluginName(query: str) -> e.g. Serum, Patcher, ...")
print()

logger = API_logging.GetLogger()
API_logging.SetLevel(API_logging.Level.info)

def OnMidiMsg(event):
    receiver.OnMidiMsg(event)

def OnSetCachedPluginCachedParameter(cachedPlugin, cachedParam, value, slot):
    logger.trace(str(value) + " " + str(slot))

    plugin = finder.firstPluginByCallName(cachedPlugin, slot)
    if plugin == -1:
        logger.warning("no plugin w/ call name '" + str(cachedPlugin) + "' found")
        return

    param = finder.firstParamByName(cachedParam, plugin, slot)
    if param == -1:
        logger.warning("no param w/ call name '" + str(cachedParam) + "' for plugin '" + str(cachedPlugin) + "' found")
        return

    OnSetParam(plugin = plugin, param = param, value = value, slot = slot)

def OnSetCachedPluginParameter(cachedPlugin, param, value, slot):
    plugin = finder.firstPluginByCallName(cachedPlugin)
    if plugin == -1:
        logger.warning("no plugin w/ call name '" + cachedPlugin + "' found")
        return

    OnSetParam(plugin, param, value, slot)

def OnSetParam(plugin, param, value, slot = -1):
    logger.info("set param '"
        + plugins.getParamName(param, plugin, slot)
        + "' of plugin '"
        + plugins.getPluginName(plugin, slot)
        + "' to '" + str(value) + "'")
    plugins.setParamValue(value, param, plugin, slot)

def OnSetMixer(track, volume):
    logger.info(str(track) + " " + str(volume))
    ui.showWindow(midi.widMixer)
    mixer.setTrackVolume(track, volume)

finder = Finder()
receiver = MidiCommunicatorReceiver(OnSetMixer, OnSetParam, OnSetCachedPluginParameter, OnSetCachedPluginCachedParameter)
