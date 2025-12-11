# tests/mock_api_server.py
from contextlib import asynccontextmanager
from unittest.mock import MagicMock, create_autospec

from fastapi import FastAPI

from pi0servo import ThreadWorker
from pi0servo.web.json_api import JsonApi, exec_cmd, read_root


class MockJsonApi(JsonApi):
    """Mocked JsonApi"""

    def __init__(self, pins, debug=False):
        """constructor"""
        self._debug = debug
        self._JsonApi__log = MagicMock()

        self.pins = pins
        self.thr_worker = create_autospec(ThreadWorker)

        self._JsonApi__log.info("Ready (Mock)")

    def end(self):
        self._JsonApi__log.info("End (Mock)")


@asynccontextmanager
async def mock_lifespan(app: FastAPI):
    """Mock lifespan for testing"""
    app.state.json_app = MockJsonApi(pins=[17, 18], debug=True)
    app.state.debug = True
    yield
    app.state.json_app.end()


def create_mock_app():
    """Create a mock FastAPI app"""
    mock_app = FastAPI(lifespan=mock_lifespan)
    mock_app.add_api_route("/", read_root, methods=["GET"])
    mock_app.add_api_route("/cmd", exec_cmd, methods=["POST"])
    return mock_app


app = create_mock_app()