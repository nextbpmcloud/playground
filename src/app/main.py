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
    """Load the chat html page"""
    return FileResponse(os.path.join(os.path.dirname(__file__), 'chat.html'))
