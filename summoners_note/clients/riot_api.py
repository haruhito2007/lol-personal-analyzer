from urllib.parse import quote

import requests

from summoners_note.errors import (
    RiotApiError,
    RiotConfigurationError,
    RiotForbiddenError,
    RiotInvalidResponseError,
    RiotNotFoundError,
    RiotRateLimitError,
    RiotTimeoutError,
    RiotUnauthorizedError,
    RiotUnavailableError,
)


class RiotApiClient:
    def __init__(
        self,
        api_key,
        regional_route,
        timeout=(3.05, 10.0),
        session=None,
    ):
        self._api_key = api_key
        self._regional_route = regional_route
        self._timeout = timeout
        self._session = session if session is not None else requests.Session()

    def get_account_by_riot_id(self, game_name, tagline):
        encoded_game_name = quote(game_name, safe="")
        encoded_tagline = quote(tagline, safe="")
        path = (
            "/riot/account/v1/accounts/by-riot-id/"
            f"{encoded_game_name}/{encoded_tagline}"
        )
        data = self._get(path)

        if not isinstance(data, dict) or not self._is_nonempty_string(
            data.get("puuid")
        ):
            raise RiotInvalidResponseError()

        return data

    def get_active_region(self, puuid):
        encoded_puuid = quote(puuid, safe="")
        path = (
            "/riot/account/v1/region/by-game/lol/by-puuid/"
            f"{encoded_puuid}"
        )
        data = self._get(path)

        required_fields = ("game", "puuid", "region")
        if not isinstance(data, dict) or any(
            not self._is_nonempty_string(data.get(field))
            for field in required_fields
        ):
            raise RiotInvalidResponseError()

        return data

    def get_match_ids_by_puuid(self, puuid, *, queue, start, count):
        encoded_puuid = quote(puuid, safe="")
        path = f"/lol/match/v5/matches/by-puuid/{encoded_puuid}/ids"
        data = self._get(
            path,
            params={
                "queue": queue,
                "start": start,
                "count": count,
            },
        )

        if not isinstance(data, list) or any(
            not self._is_nonempty_string(match_id) for match_id in data
        ):
            raise RiotInvalidResponseError()

        return data

    def get_match_detail(self, match_id):
        encoded_match_id = quote(match_id, safe="")
        path = f"/lol/match/v5/matches/{encoded_match_id}"
        data = self._get(path)

        if not isinstance(data, dict):
            raise RiotInvalidResponseError()

        return data

    def _get(self, path, params=None):
        if (
            not isinstance(self._api_key, str)
            or not self._api_key.strip()
        ):
            raise RiotConfigurationError()

        url = f"https://{self._regional_route}.api.riotgames.com{path}"
        request_options = {
            "headers": {"X-Riot-Token": self._api_key},
            "timeout": self._timeout,
        }
        if params is not None:
            request_options["params"] = params

        try:
            response = self._session.get(url, **request_options)
        except requests.Timeout as error:
            raise RiotTimeoutError() from error
        except requests.RequestException as error:
            raise RiotUnavailableError() from error

        self._raise_for_status(response)

        try:
            return response.json()
        except (TypeError, ValueError) as error:
            raise RiotInvalidResponseError() from error

    @staticmethod
    def _raise_for_status(response):
        status_code = response.status_code

        if status_code == 200:
            return
        if status_code == 401:
            raise RiotUnauthorizedError()
        if status_code == 403:
            raise RiotForbiddenError()
        if status_code == 404:
            raise RiotNotFoundError()
        if status_code == 429:
            raise RiotRateLimitError(
                retry_after=RiotApiClient._get_retry_after(response)
            )
        if 500 <= status_code < 600:
            raise RiotUnavailableError()

        raise RiotApiError()

    @staticmethod
    def _is_nonempty_string(value):
        return isinstance(value, str) and bool(value)

    @staticmethod
    def _get_retry_after(response):
        retry_after = response.headers.get("Retry-After")
        if isinstance(retry_after, str) and retry_after.isdigit():
            return retry_after
        return None
