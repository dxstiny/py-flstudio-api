# py-flstudio-api
fl studio wrapper REST-api, mixer and plugin control w/ UI

Wraps [FL Studio 20](https://www.image-line.com/) in an api, allowing you to change your mixer-inserts and plugin parameters remotely via POST requests.

## Installation
Make sure to clone the repo:
```sh
git clone https://github.com/dxstiny/py-flstudio-api.git
```
Add it to a new folder in `Documents\Image-Line\FL Studio\Settings\Hardware\My Mixer Control`

install [loopMidi](https://www.tobias-erichsen.de/software/loopmidi.html)

install [python](https://www.python.org/downloads/)

create a loopmidi port and in fl studio, add it as an input device and select API (user) as Controller type

## Usage

Run Script
```sh
python main.py
```

connect

UI http://localhost:1234/ui/mixer/
UI http://localhost:1234/ui/plugins/

POST http://localhost:1234/mixer # todo
POST http://localhost:1234/plugins # todo
