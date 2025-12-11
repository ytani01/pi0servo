# tests/conftest.py
import pytest
from click.testing import CliRunner
from fastapi.testclient import TestClient

from ._pigpio_mock import mocker_pigpio  # noqa: F403
from ._testbase_cli import (
    KEY_DOWN,
    KEY_ENTER,
    KEY_EOF,
    KEY_LEFT,
    KEY_RIGHT,
    KEY_UP,
    CLITestBase,
    InteractiveSession,
)

# This is necessary to make the fixtures available to all tests.
(
    CLITestBase,
    InteractiveSession,
    KEY_UP,
    KEY_DOWN,
    KEY_ENTER,
    KEY_EOF,
    KEY_LEFT,
    KEY_RIGHT,
    mocker_pigpio,
)


@pytest.fixture
def mock_api_server_app():
    """Fixture to provide the mock FastAPI app."""
    from .mock_api_server import app

    return app


@pytest.fixture
def api_client(mock_api_server_app):
    """Fixture to provide a TestClient for the mock API server."""
    with TestClient(mock_api_server_app) as client:
        yield client


@pytest.fixture
def cli_runner():
    """Fixture to provide a CLITestBase instance."""
    return CLITestBase()


@pytest.fixture
def click_runner():
    """Fixture to provide a Click CliRunner."""
    return CliRunner()
