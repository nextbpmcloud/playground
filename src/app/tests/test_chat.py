import asyncio
import pytest
import socketio
import uvicorn

from ..main import app

PORT = 5000

server = None
server_task = None


def get_server():
    config = uvicorn.Config(app, host='localhost', port=PORT)
    server = uvicorn.Server(config=config)
    config.setup_event_loop()
    return server


@pytest.fixture
async def async_get_server():
    global server
    global server_task
    print("Starting server")
    server = get_server()
    server_task = server.serve()
    asyncio.ensure_future(server_task)
    asyncio.sleep(1)


@pytest.mark.asyncio
async def test_websocket(async_get_server):
    sio = socketio.AsyncClient()

    @sio.on('chat message')
    def message(data):
        print(f"Client received: {data}")

    await sio.connect(f'http://localhost:{PORT}', socketio_path='/sio/socket.io/')
    await sio.emit('chat message', 'HOLA!')
    await sio.disconnect()
    server.should_exit = True
    await server_task.close()
    asyncio.get_running_loop().stop()
