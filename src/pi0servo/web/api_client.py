#
# (c) 2025 Yoichi Tanibayashi
#
"""API Client."""
import json
import requests

from pi0servo import get_logger


class ApiClient:
    """API Client.

    POST method
    """

    DEF_URL = "http://localhost:8000/cmd"
    HEADERS = {"content-type": "application/json"}

    def __init__(self, url=DEF_URL, debug=False) -> None:
        """Constractor."""
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("url=%s", url)

        self.url = url

    def post(self, data_str: str):
        """Send command line string."""

        try:
            res = requests.post(self.url, data=data_str, headers=self.HEADERS)
            self.__log.debug("res=%s", res)
        except Exception as _e:
            _msg = f"{type(_e).__name__}: {_e}"
            self.__log.error(_msg)
            return {"error": _msg}

        return res

    def get_result_json(self, result) -> dict:
        """Get JSON date from result"""
        try:
            result_json = result.json()
        except Exception as _e:
            result_json = json.loads(
                f'{"error": "{type(_e).__name__}: {_e}"}'
            )
        self.__log.debug("result_json=%s", result_json)
        return result_json
