"""The FastAPI main module"""
import os
import socketio

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel, Field

NAME = 'Test API'
VERSION = '0.1'

app = FastAPI(title=NAME, version=VERSION)
path = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=os.path.join(path, "static")), name="static")

sio = socketio.AsyncServer(async_mode='asgi')
# socketio adds automatically /socket.io/ to the URL.
app.mount('/sio', socketio.ASGIApp(sio))


@sio.on('connect')
def sio_connect(sid, environ):      # pylint: disable=unused-argument
    """Track user connection"""
    print('A user connected')


@sio.on('disconnect')
def sio_disconnect(sid):            # pylint: disable=unused-argument
    """Track user disconnection"""
    print('User disconnected')


@sio.on('chat message')
async def chat_message(sid, msg):   # pylint: disable=unused-argument
    """Receive a chat message and send to all clients"""
    print(f"Server received and sends to all clients: {msg}")
    await sio.emit('chat message', msg)


class VersionInfo(BaseModel):
    """The version info model"""
    name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")

    class Config:
        schema_extra = {
            "example": {
                "name": NAME,
                "version": VERSION,
            }
        }


@app.get("/", response_model=VersionInfo)
async def home():
    """Get version info"""
    res = VersionInfo(
        name=NAME,
        version=VERSION,
    )
    return res


class EchoRequestResponse(BaseModel):
    """Echo response model"""
    message: str


@app.get("/echo", response_model=EchoRequestResponse)
async def echo_get(message: str):
    """Echo text gotten from query string with get method"""
    return EchoRequestResponse(message=message)


@app.post("/echo", response_model=EchoRequestResponse)
async def echo_post(message: EchoRequestResponse):
    """Echo text gotten from body with post method"""
    return EchoRequestResponse(message=message.message)


@app.get("/chat", response_class=FileResponse)
def chat() -> FileResponse:
    """Load the chat html page"""
    return FileResponse(os.path.join(os.path.dirname(__file__), 'chat.html'))
