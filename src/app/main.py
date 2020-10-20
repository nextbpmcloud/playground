"""The FastAPI main module"""
import os
import socketio

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
path = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=os.path.join(path, "static")), name="static")

sio = socketio.AsyncServer(async_mode='asgi')
app.mount('/sio', socketio.ASGIApp(sio))  # socketio adds automatically /socket.io/ to the URL.


@sio.on('connect')
def sio_connect(sid, environ):
    """A user / browser tab has connected"""
    print('A user connected')


@sio.on('disconnect')
def sio_disconnect(sid):
    """A user / browser tab has disconnected"""
    print('User disconnected')


@sio.on('chat message')
async def chat_message(sid, msg):
    """A chat message has arrived"""
    print('Message: %s' % msg)
    await sio.emit('chat message', msg)


@app.get("/")
async def home() -> dict:
    """Check if system is alive and get version info"""
    return {
        'name': "Test Service",
        'message': "Hello world",
        'version': "0.1",
    }


@app.get("/chat", response_class=FileResponse)
def chat() -> FileResponse:
    return FileResponse(os.path.join(os.path.dirname(__file__), 'chat.html'))
