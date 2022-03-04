"""
The example from the README
"""

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi_sio import FastAPISIO

class PurrModel(BaseModel):
    detail: str
    loudness: int

class BellyRubModel(BaseModel):
    where_exactly: str
    scratches_num: int

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