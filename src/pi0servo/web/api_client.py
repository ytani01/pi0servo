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

    def mk_result_json(
        self,
        status: str,
        cmddata: str | dict | list[dict],
        retval: str | dict | None = None
    ) -> dict:
        """Make result data (JSON, dict)"""

        if isinstance(cmddata, str):
            cmddata = json.loads(cmddata)

        _result = {
            "status": status,
            "cmddata": cmddata,
            "retval": retval,
        }
        self.__log.debug("result=%s", _result)
        return _result

    def post(self, data_json) -> dict:
        """Send command line string."""

        try:
            post_data = json.dumps(data_json)
            self.__log.debug("post_data=%a", post_data)

            res = requests.post(
                self.url, data=post_data, headers=self.HEADERS
            )
            self.__log.debug("res=%s", json.dumps(res.json()))
            return res.json()

        except requests.exceptions.ConnectionError as _e:
            _msg = f"{type(_e).__name__}: {_e}"
            self.__log.debug(_msg)
            return self.mk_result_json("ERR", data_json, _msg)

        except Exception as _e:
            _msg = f"{type(_e).__name__}: {_e}"
            self.__log.error(_msg)
            return self.mk_result_json("ERR", data_json, _msg)
