import asyncio
from aiohttp import web
from aiohttp_index import IndexMiddleware

import time
import pygame.midi

pygame.midi.init()
player = pygame.midi.Output(4)

'''
functions:
0: setMixer(byte1: mixer, byte2:volume)
1: setPluginParameter(byte1: plugin, byte2: value, nibble3: parameter) // max parameter: 15
2: cachePluginIndex(byte1: char[x] lsbs, byte2: char[x] msbs)
3: cacheParameterIndex(byte1: char[x] lsbs, byte2: char[x] msbs)
4: setCachedPluginParameter(byte1: value, byte2: parameter)
5: setCachedPluginParameter(byte1: value)
'''

def setmixer(track, value):
    value = 100 if value > 100 else value
    print(track, value)
    startMessage(0)
    send_bytes(track, value)
    stopMessage(0)

async def postMixer(request: web.Request):
    value = await request.json()
    setmixer(int(value["mixer"]), int(value["volume"]))
    return web.Response(status = 200, text = "success!")

def setiplugin(plugin, param, value):
    value = 100 if value > 100 else value
    startMessage(1)
    send_bytes(plugin, value, param)
    stopMessage(1)

def setsplugin(plugin, param, value, slot):
    startMessage(2)
    send_string(plugin)
    stopMessage(2)

    startMessage(3)
    send_string(param)
    stopMessage(3)

    startMessage(5)
    send_bytes(value, 127 if slot == -1 else 0)
    stopMessage(5)

async def postIPlugin(request: web.Request):
    value = await request.json()
    setiplugin(int(value["plugin"]), int(value["param"]), int(value["value"]))
    return web.Response(status = 200, text = "success!")

async def postSPlugin(request: web.Request):
    value = await request.json()
    setsplugin(value["plugin"], value["param"], int(value["value"]), int(value["slot"]))
    return web.Response(status = 200, text = "success!")

def stopMessage(function: int):
    send_bytes(127, function)

def startMessage(function: int, additional = 0):
    send_bytes(126, function, additional)

def send_string(string: str):
    if type(string) is int:
        char = string
        byte1 = 127 if char > 127 else char
        byte2 = char - 127 if char > 127 else 0
        print(byte1, byte2)
        send_bytes(byte1, byte2)
        return

    for i in range(len(string)):
        char = ord(string[i])
        byte1 = 127 if char > 127 else char
        byte2 = char - 127 if char > 127 else 0
        print(byte1, byte2)
        send_bytes(byte1, byte2)

def send_bytes(byte1: int, byte2: int, nibble3 = 0):
    # nibble1: note, nibble2: velocity, nibble3: channel
    player.note_on(byte1, byte2, nibble3)
    #time.sleep(0.1)
    player.note_off(byte1, 0, nibble3)

app = web.Application(middlewares=[IndexMiddleware()])
app.router.add_post('/mixer', postMixer)
app.router.add_post('/iplugins', postIPlugin)
app.router.add_post('/plugins', postSPlugin)
app.router.add_static('/', './www')
asyncio.run ( web._run_app(app, port=1234) )

player.close()