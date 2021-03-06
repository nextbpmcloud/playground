"""Some python-socketio tests"""
from typing import Any, List, Optional, Awaitable
# stdlib imports
import asyncio
import os

# 3rd party imports
import pytest
import socketio
import uvicorn

# FastAPI imports
from fastapi import FastAPI
from fastapi.testclient import TestClient

# project importsn
from .. import main

PORT = 8000
LISTENING_IF = '127.0.0.1'
BASE_URL = f'http://{LISTENING_IF}:{PORT}'

# deactivate monitoring task in python-socketio to avoid errores during shutdown
main.sio.eio.start_service_task = False
client = TestClient(main.app)


class UvicornTestServer(uvicorn.Server):
    """Uvicorn test server

    Usage:
        @pytest.fixture
        server = UvicornTestServer()
        await server.up()
        yield
        await server.down()
    """

    def __init__(self, app: FastAPI = main.app, host: str = LISTENING_IF, port: int = PORT):
        """Create a Uvicorn test server

        Args:
            app (FastAPI, optional): the FastAPI app. Defaults to main.app.
            host (str, optional): the host ip. Defaults to '127.0.0.1'.
            port (int, optional): the port. Defaults to PORT.
        """
        self._startup_done = asyncio.Event()
        self._serve_task: Optional[Awaitable[Any]] = None
        super().__init__(config=uvicorn.Config(app, host=host, port=port))

    async def startup(self, sockets: Optional[List] = None) -> None:
        """Override uvicorn startup"""
        await super().startup(sockets=sockets)
        self.config.setup_event_loop()
        self._startup_done.set()

    async def start_up(self) -> None:
        """Start up server asynchronously"""
        self._serve_task = asyncio.create_task(self.serve())
        await self._startup_done.wait()

    async def tear_down(self) -> None:
        """Shut down server asynchronously"""
        self.should_exit = True
        if self._serve_task:
            await self._serve_task


@pytest.fixture
async def startup_and_shutdown_server():    # pylint: disable=unused-variable
    """Start server as test fixture and tear down after test"""
    server = UvicornTestServer()
    await server.start_up()
    yield
    await server.tear_down()


@pytest.mark.asyncio
async def test_chat_simple(startup_and_shutdown_server):  # pylint: disable=unused-argument,redefined-outer-name
    """A simple websocket test"""

    sio = socketio.AsyncClient()
    future = asyncio.get_running_loop().create_future()

    @sio.on('chat message')
    def on_message_received(data):          # pylint: disable=unused-variable
        print(f"Client received: {data}")
        # set the result
        future.set_result(data)

    message = 'Hello!'
    await sio.connect(BASE_URL, socketio_path='/sio/socket.io/')
    print(f"Client sends: {message}")
    await sio.emit('chat message', message)
    # wait for the result to be set (avoid waiting forever)
    await asyncio.wait_for(future, timeout=1.0)
    await sio.disconnect()
    assert future.result() == message


def test_chat_page():
    """Check if chat page returns contents"""
    response = client.get("/chat")
    assert response.ok
    filename = os.path.join(os.path.dirname(__file__), '..', 'chat.html')
    print(f"Chat page: {filename}")
    with open(filename, 'rb') as page:
        assert response.content == page.read()


@pytest.mark.asyncio
async def test_chat_page2(startup_and_shutdown_server):
    """Check if chat page returns contents"""
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL + '/chat') as response:
            assert response.status == 200
            content = await response.text()
            assert 'socket.io' in content
            assert 'chat' in content
