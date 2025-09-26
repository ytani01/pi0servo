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
        cmddata: str | dict,
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

    def post(self, data_str: str):
        """Send command line string."""

        try:
            res = requests.post(self.url, data=data_str, headers=self.HEADERS)
            self.__log.debug("res=%s", res.json())

        except requests.exceptions.ConnectionError as _e:
            _msg = f"{type(_e).__name__}: {_e}"
            self.__log.debug(_msg)
            return self.mk_result_json("ERR", data_str, _msg)

        except Exception as _e:
            _msg = f"{type(_e)}: {_e}"
            self.__log.error(_msg)
            return self.mk_result_json("ERR", data_str, _msg)

        return res

    def get_result_json(self, result) -> dict | list[dict]:
        """Get JSON date from result"""
        try:
            result_json = result.json()

        except Exception as _e:
            if isinstance(result, dict) and result.get("status"):
                result_json = result
            else:
                err_msg = f"{type(_e).__name__}: {_e}"
                result_json = self.mk_result_json("ERR", "", err_msg)

        if isinstance(result_json, list):
            _res2 = []
            for r in result_json:
                if isinstance(r, str):
                    _res2.append(json.loads(r))
                else:
                    _res2.append(r)

            if len(_res2) == 1:
                result_json = _res2[0]
            else:
                result_json = _res2

        self.__log.debug("result_json=%s", result_json)
        return result_json
