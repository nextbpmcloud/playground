import socketio

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

sio = socketio.AsyncServer(async_mode='asgi')
app.mount('/sio', socketio.ASGIApp(sio))


@sio.on('connect')
def sio_connect(sid, environ):
    print('A user connected')


@sio.on('disconnect')
def sio_disconnect(sid):
    print('User disconnected')


@sio.on('chat message')
async def chat_message(sid, msg):
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
def chat() -> HTMLResponse:
    return FileResponse('chat.html')
