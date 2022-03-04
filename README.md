# fastapi-sio

![FastAPI library](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white)
![Socket.io](https://img.shields.io/badge/-Socket.io-black?logo=socket.io&logoColor=white)
![Uses AsyncAPI](https://img.shields.io/badge/-AsyncAPI-4f8fbe)
![Current state](https://img.shields.io/badge/status-prerelease-orange)

**Socket.io FastAPI integration library with first-class documentation using AsyncAPI**

The usage of the library is very familiar to the experience you‘re used to in FastAPI. Automatic documentation, type hints everywhere and heavy use of Pydantic.

## Features

- First-class generated specification & documentation
- Uses [python_socketio](https://python-socketio.readthedocs.io/en/latest/) underneath
- Fully typed using pydantic, including the [AsyncAPI spec](./fastapi_sio/schemas/asyncapi.py)
- Streamlined emit to clients ([learn more in docs](./docs/emitting.md))
- Forces strictly to emit correct data type  ([see the example](./docs/example.md))

## What‘s Missing?
  
- [ ] Serve AsyncAPI studio at /sio/docs
    - Unfortunately, AsyncAPI studio doesn‘t work the same way as Swagger UI, there is currently no way to use CDN hosted built package and supply only single html file and URL with spec JSON
- [ ] Support for more obscure fields of AsyncAPI, such as `traits`, ...

## Usage Example

```python
fastapi_app = FastAPI()
sio_app = FastAPISIO(app=fastapi_app)

purr_channel = sio_app.create_emitter(
    "purrs",
    model=PurrModel,
    summary="Channel for purrs",
    description="Receive any purrs here!",
)

@sio_app.on(
    "rubs",
    model=BellyRubModel,
    summary="Channel for belly rubs",
    description="Send your belly rubs through here!",
)
async def handle_rub(sid, data):
    await purr_channel.emit(
        PurrModel(loudness=2, detail="Purr for all listeners")
    )
    return "Ack to the one who rubbed"
```

👉 [Check out the example AsyncAPI documentation output!](https://studio.asyncapi.com/?url=https://raw.githubusercontent.com/marianhlavac/fastapi-sio/master/examples/from_readme_asyncapi.json)

By default (you can change these values):
 - the Socket.io endpoint path is **`/sio/socket.io`** (the `socket.io` part is set automatically by some clients)
 - The AsyncAPI spec file is at **`/sio/docs/asyncapi.json`**

Find more in the [examples](/docs/examples.md).

## Documentation & Reference

Refer to the [/docs](./docs/index.md) directory to learn how to use this library in your project.

_TODO: This documentation will be hosted on Github Pages in the near future, hopefully._


## Contribution

...

## Used by

<a href="https://dronetag.cz"><img src="https://dronetag.cz/assets/logo-full.svg" height="32" /></a>

[Feel free to open a PR](https://github.com/marianhlavac/fastapi-sio/pulls) to add your project or company to this list.