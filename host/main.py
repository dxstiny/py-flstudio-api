# url=https://github.com/dxstiny/py-flstudio-api/
# author=dxstiny

import asyncio
from aiohttp import web
from aiohttp_index import IndexMiddleware

from MidiCommunicator import MidiCommunicator

midiCommunicator = MidiCommunicator()

async def postMixer(request: web.Request):
    value = await request.json()
    midiCommunicator.setmixer(int(value["mixer"]), int(value["volume"]))
    return web.Response(status = 200, text = "success")

def setsplugin(plugin, param, value, slot):
    midiCommunicator.cachePluginIndex(plugin)
    midiCommunicator.cacheParameterIndex(param)
    midiCommunicator.setCachedPluginCachedParameter(value, slot)

async def postSPlugin(request: web.Request):
    value = await request.json()
    text = midiCommunicator.setPluginParameter(value["plugin"], int(value["value"]), value["param"], int(value["slot"]))
    return web.Response(status = 200, text = text)

app = web.Application(middlewares=[IndexMiddleware()])
app.router.add_post('/mixer', postMixer)
app.router.add_post('/plugins', postSPlugin)
app.router.add_static('/', './www')
asyncio.run ( web._run_app(app, port=1234) )
