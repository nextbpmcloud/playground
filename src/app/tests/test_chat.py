import asyncio
import pytest
import socketio
import uvicorn

from .. import main

PORT = 5000


def get_server():
    """Get a complete server instance"""
    config = uvicorn.Config(main.app, host='127.0.0.1', port=PORT)
    server = uvicorn.Server(config=config)
    # deactivate monitoring task to avoid errores during shutdown
    main.sio.eio.start_service_task = False
    config.setup_event_loop()
    return server


async def wait_ready(server, interval=0.05, max_wait=5):
    """Wait for the server to be ready"""
    i = 0
    while not server.started:
        await asyncio.sleep(interval)
        i += interval
        if i > max_wait:
            raise RuntimeError(f"Server couldn't startup in {max_wait} seconds")


@pytest.fixture
async def async_get_server():
    """Start server as test fixture and tear down after test"""
    server = get_server()
    serve_task = asyncio.create_task(server.serve())
    await wait_ready(server)
    yield
    # teardown code
    server.should_exit = True
    await serve_task   # allow server run tasks before shut down


@pytest.mark.asyncio
async def test_chat_simple(async_get_server):
    """A simple websocket test"""

    class Result:
        """Generic message result"""
        # add any attributes you need
        message_received = False
        message = None

    sio = socketio.AsyncClient()
    result = Result()

    @sio.on('chat message')
    def on_message_received(data):
        print(f"Client received: {data}")
        result.message_received = True
        result.message = data

    message = 'Hello!'
    await sio.connect(f'http://localhost:{PORT}', socketio_path='/sio/socket.io/')
    print(f"Client sends: {message}")
    await sio.emit('chat message', message)
    await sio.sleep(0.1)
    await sio.disconnect()
    assert result.message_received is True
    assert result.message == message
