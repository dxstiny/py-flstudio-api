# url=https://github.com/dxstiny/py-flstudio-api/
# author=dxstiny

import plugins
import channels
import API_logging

class Finder():
    def __init__(self):
        self._logger = API_logging.GetLogger("finder")

    def firstParamByName(self, query, plugin, slot):
        count = plugins.getParamCount(plugin, slot)
        for i in range(count):
            if query.lower() in plugins.getParamName(i, plugin, slot).lower():
                self._logger.debug(plugins.getParamName(i, plugin, slot))
                return i
        return -1

    def firstPluginByCallName(self, query, slot = -1):
        if slot is not -1:
            self._logger.info("slot is not -1, taking " + str(ord(query)))
            return ord(query)

        count = channels.channelCount(1)

        for i in range(count):
            self._logger.debug(channels.getChannelName(i))
            if query.lower() in channels.getChannelName(i).lower():
                try:
                    self._logger.debug(plugins.getPluginName(i) + " named " + channels.getChannelName(i))
                    return i
                except:
                    pass
        return -1

    def firstPluginByPluginName(self, query):
        count = channels.channelCount(1)

        for i in range(count):
            try:
                if query.lower() in plugins.getPluginName(i).lower():
                    self._logger.trace(plugins.getPluginName(i))
                    return i
            except TypeError:
                pass
        return -1
