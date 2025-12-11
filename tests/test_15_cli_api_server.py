import json
import time
from unittest.mock import MagicMock

import pytest

CMD = "uv run pi0servo api-server"
PIN = 5


@pytest.mark.skip(
    reason="CLI server startup test is unstable due to uv run overhead"
)
class TestBasic:
    """Basic tests for CLI server startup."""

    def test_start(self, cli_runner):
        """server start"""

        cmdline = f"{CMD} {PIN}"
        print(f"* cmdline='{cmdline}'")

        session = cli_runner.run_interactive_command(cmdline)

        assert session.expect("Ready")

        session.close()
        time.sleep(1)

    def test_start_err(self, cli_runner):
        """server start error"""

        cmdline = CMD
        print(f"* cmdline='{cmdline}'")

        result = cli_runner.run_command(cmdline)
        print(f"stdout='{result.stdout}'")
        print(f"stderr='{result.stderr}'")

        cli_runner.assert_output_contains(result, stdout="Error")
        cli_runner.assert_output_contains(result, stdout="Usage")
        cli_runner.assert_output_contains(result, stdout="Options")


class TestApiEndpoints:
    """Tests for API endpoints using TestClient."""

    def test_read_root(self, api_client):
        """Test GET / endpoint."""
        response = api_client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}

    def test_exec_cmd_single_success(self, api_client, mock_api_server_app):
        """Test POST /cmd with a single valid command."""
        # Setup mock response from ThreadWorker
        mock_json_app = mock_api_server_app.state.json_app
        mock_thr_worker = mock_json_app.thr_worker
        mock_thr_worker.send.return_value = {"id": 1, "result": 90.0, "error": None}

        cmd = {"method": "get_angle", "params": [17], "id": 1}
        response = api_client.post("/cmd", json=cmd)

        assert response.status_code == 200
        assert response.json() == {"id": 1, "result": 90.0, "error": None}
        mock_thr_worker.send.assert_called_once_with(cmd)

    def test_exec_cmd_multiple_success(self, api_client, mock_api_server_app):
        """Test POST /cmd with multiple valid commands."""
        mock_json_app = mock_api_server_app.state.json_app
        mock_thr_worker = mock_json_app.thr_worker
        mock_thr_worker.send.side_effect = [
            {"id": 1, "result": 90.0, "error": None},
            {"id": 2, "result": -90.0, "error": None},
        ]

        cmds = [
            {"method": "get_angle", "params": [17], "id": 1},
            {"method": "get_angle", "params": [18], "id": 2},
        ]
        response = api_client.post("/cmd", json=cmds)

        assert response.status_code == 200
        assert response.json() == [
            {"id": 1, "result": 90.0, "error": None},
            {"id": 2, "result": -90.0, "error": None},
        ]
        assert mock_thr_worker.send.call_count == 2

    def test_exec_cmd_invalid_json(self, api_client):
        """Test POST /cmd with invalid JSON."""
        response = api_client.post(
            "/cmd",
            headers={"Content-Type": "application/json"},
            data="{invalid json",
        )
        assert response.status_code == 422

    def test_exec_cmd_rpc_error(self, api_client, mock_api_server_app):
        """Test POST /cmd that results in a JSON-RPC error."""
        mock_json_app = mock_api_server_app.state.json_app
        mock_thr_worker = mock_json_app.thr_worker
        error_response = {
            "id": 3,
            "result": None,
            "error": {"code": -32602, "message": "Invalid params"},
        }
        mock_thr_worker.send.return_value = error_response

        cmd = {"method": "set_angle", "id": 3}  # Missing 'params'
        response = api_client.post("/cmd", json=cmd)

        assert response.status_code == 200
        assert response.json() == error_response
        mock_thr_worker.send.assert_called_once_with(cmd)
