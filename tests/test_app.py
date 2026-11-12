import unittest
from unittest.mock import Mock, call, patch

import requests

from summoners_note import create_app
from summoners_note.clients.riot_api import RiotApiClient
from summoners_note.errors import (
    InvalidRiotIdError,
    ParticipantNotFoundError,
    PlayerNotFoundError,
    RegionLookupNotFoundError,
    RegionResponseMismatchError,
    RegionUnconfirmedError,
    RiotConfigurationError,
    RiotForbiddenError,
    RiotInvalidResponseError,
    RiotNotFoundError,
    RiotRateLimitError,
    RiotTimeoutError,
    RiotUnauthorizedError,
    RiotUnavailableError,
    UnexpectedQueueError,
)
from summoners_note.services.player_search import PlayerSearchService


def build_match_detail(
    *,
    puuid="target-puuid",
    queue_id=420,
    champion_name="Ahri",
    win=True,
    kills=10,
    deaths=2,
    assists=8,
):
    return {
        "info": {
            "queueId": queue_id,
            "participants": [
                {
                    "puuid": puuid,
                    "championName": champion_name,
                    "win": win,
                    "kills": kills,
                    "deaths": deaths,
                    "assists": assists,
                }
            ],
        }
    }


class ApplicationFactoryTest(unittest.TestCase):
    def setUp(self):
        self.riot_api_client = Mock(spec=RiotApiClient)
        self.app = create_app(
            {
                "TESTING": True,
                "RIOT_API_KEY": "test-secret-api-key",
            },
            riot_api_client=self.riot_api_client,
        )
        self.client = self.app.test_client()

    def configure_successful_search(self):
        self.riot_api_client.get_account_by_riot_id.return_value = {
            "puuid": "test-puuid",
        }
        self.riot_api_client.get_active_region.return_value = {
            "game": "lol",
            "puuid": "test-puuid",
            "region": "jp1",
        }
        self.riot_api_client.get_match_ids_by_puuid.return_value = [
            "JP1_test-match-id",
        ]
        self.riot_api_client.get_match_detail.return_value = (
            build_match_detail(puuid="test-puuid")
        )

    def test_create_app_uses_test_config(self):
        self.assertTrue(self.app.config["TESTING"])
        self.assertFalse(self.app.config["DEBUG"])

    def test_top_page_and_static_files_are_available(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"/static/css/style.css", response.data)
        self.assertIn(b"/static/js/main.js", response.data)
        self.assertIn(b'id="search-form"', response.data)
        self.assertIn(b'id="loading-state"', response.data)
        self.assertIn(b'id="message-state"', response.data)
        self.assertIn(b'id="no-match-state"', response.data)
        self.assertIn(b'id="result-section"', response.data)

        css_response = self.client.get("/static/css/style.css")
        javascript_response = self.client.get("/static/js/main.js")

        self.assertEqual(css_response.status_code, 200)
        self.assertEqual(javascript_response.status_code, 200)
        css_response.close()
        javascript_response.close()

    def test_javascript_contains_safe_state_and_rendering_controls(self):
        response = self.client.get("/static/js/main.js")
        javascript = response.get_data(as_text=True)

        self.assertIn('fetch("/search"', javascript)
        self.assertIn("response.ok", javascript)
        self.assertIn("textContent", javascript)
        self.assertIn("searchButton.disabled", javascript)
        self.assertIn("match.kda.toFixed(2)", javascript)
        self.assertNotIn("console.log", javascript)
        self.assertNotIn("innerHTML", javascript)
        response.close()

    @patch("requests.sessions.Session.get")
    def test_search_returns_latest_match_without_external_http(
        self,
        session_get,
    ):
        self.configure_successful_search()

        response = self.client.post(
            "/search",
            json={"gameName": "TestPlayer", "tagline": "JP1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "gameName": "TestPlayer",
                "tagline": "JP1",
                "latestMatch": {
                    "championName": "Ahri",
                    "win": True,
                    "kills": 10,
                    "deaths": 2,
                    "assists": 8,
                    "kda": 9.0,
                    "zeroDeaths": False,
                },
            },
        )
        self.assertEqual(
            self.riot_api_client.method_calls,
            [
                call.get_account_by_riot_id("TestPlayer", "JP1"),
                call.get_active_region("test-puuid"),
                call.get_match_ids_by_puuid(
                    "test-puuid",
                    queue=420,
                    start=0,
                    count=1,
                ),
                call.get_match_detail("JP1_test-match-id"),
            ],
        )
        session_get.assert_not_called()
        self.assertNotIn(b"test-secret-api-key", response.data)
        self.assertNotIn(b"test-puuid", response.data)

    def test_invalid_json_or_riot_id_returns_safe_error(self):
        cases = (
            {"data": "not-json", "content_type": "application/json"},
            {"json": {"gameName": "", "tagline": "JP1"}},
            {"json": {"gameName": "TestPlayer", "tagline": None}},
        )

        for request_arguments in cases:
            with self.subTest(request_arguments=request_arguments):
                self.riot_api_client.reset_mock()

                response = self.client.post("/search", **request_arguments)

                self.assertEqual(response.status_code, 400)
                self.assertEqual(
                    response.get_json()["error"]["code"],
                    "invalid_riot_id",
                )
                self.riot_api_client.get_account_by_riot_id.assert_not_called()

    def test_no_solo_duo_match_returns_http_200_with_null_match(self):
        self.configure_successful_search()
        self.riot_api_client.get_match_ids_by_puuid.return_value = []

        response = self.client.post(
            "/search",
            json={"gameName": "TestPlayer", "tagline": "JP1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.get_json()["latestMatch"])
        self.riot_api_client.get_match_detail.assert_not_called()

    def test_unconfirmed_region_returns_safe_error_without_match_request(self):
        self.riot_api_client.get_account_by_riot_id.return_value = {
            "puuid": "sensitive-test-puuid",
        }
        self.riot_api_client.get_active_region.return_value = {
            "game": "lol",
            "puuid": "sensitive-test-puuid",
            "region": "unverified-region",
        }

        response = self.client.post(
            "/search",
            json={"gameName": "TestPlayer", "tagline": "TEST"},
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.get_json()["error"]["code"],
            "region_unconfirmed",
        )
        self.riot_api_client.get_match_ids_by_puuid.assert_not_called()
        self.assertNotIn(b"sensitive-test-puuid", response.data)
        self.assertNotIn(b"unverified-region", response.data)
        self.assertNotIn(b"test-secret-api-key", response.data)

    def test_rate_limit_returns_retry_after_without_match_request(self):
        self.riot_api_client.get_account_by_riot_id.return_value = {
            "puuid": "test-puuid",
        }
        self.riot_api_client.get_active_region.side_effect = (
            RiotRateLimitError(retry_after="12")
        )

        response = self.client.post(
            "/search",
            json={"gameName": "TestPlayer", "tagline": "TEST"},
        )

        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers["Retry-After"], "12")
        self.assertEqual(
            response.get_json()["error"]["code"],
            "riot_api_rate_limited",
        )
        self.riot_api_client.get_match_ids_by_puuid.assert_not_called()

    @patch("requests.sessions.Session.get")
    def test_missing_api_key_returns_safe_error_without_http_request(
        self,
        session_get,
    ):
        app = create_app(
            {
                "TESTING": True,
                "RIOT_API_KEY": None,
            }
        )
        client = app.test_client()

        response = client.post(
            "/search",
            json={"gameName": "TestPlayer", "tagline": "JP1"},
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.get_json()["error"]["code"],
            "riot_api_configuration_error",
        )
        session_get.assert_not_called()
        self.assertNotIn(b"RIOT_API_KEY", response.data)

    def test_api_failures_return_safe_json(self):
        cases = (
            (RiotUnauthorizedError(), 503, "riot_api_unauthorized"),
            (RiotForbiddenError(), 503, "riot_api_forbidden"),
            (RiotTimeoutError(), 504, "riot_api_timeout"),
            (RiotUnavailableError(), 503, "riot_api_unavailable"),
            (
                RiotInvalidResponseError(),
                502,
                "riot_api_invalid_response",
            ),
        )

        for error, status_code, error_code in cases:
            with self.subTest(error=type(error).__name__):
                self.riot_api_client.reset_mock()
                self.riot_api_client.get_account_by_riot_id.side_effect = (
                    error
                )

                response = self.client.post(
                    "/search",
                    json={"gameName": "TestPlayer", "tagline": "JP1"},
                )

                self.assertEqual(response.status_code, status_code)
                self.assertEqual(
                    response.get_json()["error"]["code"],
                    error_code,
                )
                self.assertNotIn(b"test-secret-api-key", response.data)
                self.assertNotIn(b"test-puuid", response.data)


class PlayerSearchServiceTest(unittest.TestCase):
    def setUp(self):
        self.riot_api_client = Mock(spec=RiotApiClient)
        self.riot_api_client.get_account_by_riot_id.return_value = {
            "puuid": "target-puuid",
        }
        self.riot_api_client.get_active_region.return_value = {
            "game": "lol",
            "puuid": "target-puuid",
            "region": "jp1",
        }
        self.riot_api_client.get_match_ids_by_puuid.return_value = [
            "JP1_test-match-id",
        ]
        self.riot_api_client.get_match_detail.return_value = (
            build_match_detail()
        )
        self.service = PlayerSearchService(self.riot_api_client)

    def test_jp1_search_returns_target_participant_stats_and_kda(self):
        result = self.service.search("TestPlayer", "JP1")

        self.assertEqual(
            result["latestMatch"],
            {
                "championName": "Ahri",
                "win": True,
                "kills": 10,
                "deaths": 2,
                "assists": 8,
                "kda": 9.0,
                "zeroDeaths": False,
            },
        )
        self.assertEqual(
            self.riot_api_client.method_calls,
            [
                call.get_account_by_riot_id("TestPlayer", "JP1"),
                call.get_active_region("target-puuid"),
                call.get_match_ids_by_puuid(
                    "target-puuid",
                    queue=420,
                    start=0,
                    count=1,
                ),
                call.get_match_detail("JP1_test-match-id"),
            ],
        )

    def test_zero_deaths_uses_kills_plus_assists_without_division(self):
        self.riot_api_client.get_match_detail.return_value = (
            build_match_detail(kills=7, deaths=0, assists=11)
        )

        result = self.service.search("TestPlayer", "JP1")

        self.assertEqual(result["latestMatch"]["kda"], 18.0)
        self.assertTrue(result["latestMatch"]["zeroDeaths"])

    def test_no_solo_duo_match_returns_normal_empty_result(self):
        self.riot_api_client.get_match_ids_by_puuid.return_value = []

        result = self.service.search("TestPlayer", "JP1")

        self.assertIsNone(result["latestMatch"])
        self.riot_api_client.get_match_detail.assert_not_called()

    def test_invalid_riot_id_stops_before_api_request(self):
        invalid_values = (
            (None, "JP1"),
            (123, "JP1"),
            ("TestPlayer", None),
            ("TestPlayer", []),
            ("", "JP1"),
            ("   ", "JP1"),
            ("TestPlayer", "   "),
            ("Test\nPlayer", "JP1"),
            ("TestPlayer", "JP\t1"),
        )

        for game_name, tagline in invalid_values:
            with self.subTest(game_name=game_name, tagline=tagline):
                self.riot_api_client.reset_mock()

                with self.assertRaises(InvalidRiotIdError):
                    self.service.search(game_name, tagline)

                self.riot_api_client.get_account_by_riot_id.assert_not_called()

    def test_missing_riot_id_is_reported_as_player_not_found(self):
        self.riot_api_client.get_account_by_riot_id.side_effect = (
            RiotNotFoundError()
        )

        with self.assertRaises(PlayerNotFoundError):
            self.service.search("MissingPlayer", "TEST")

        self.riot_api_client.get_active_region.assert_not_called()
        self.riot_api_client.get_match_ids_by_puuid.assert_not_called()

    def test_region_404_stops_match_request(self):
        self.riot_api_client.get_active_region.side_effect = (
            RiotNotFoundError()
        )

        with self.assertRaises(RegionLookupNotFoundError):
            self.service.search("TestPlayer", "TEST")

        self.riot_api_client.get_match_ids_by_puuid.assert_not_called()

    def test_unconfirmed_region_stops_match_request(self):
        self.riot_api_client.get_active_region.return_value["region"] = "kr"

        with self.assertRaises(RegionUnconfirmedError):
            self.service.search("TestPlayer", "TEST")

        self.riot_api_client.get_match_ids_by_puuid.assert_not_called()

    def test_mismatched_game_or_puuid_stops_match_request(self):
        mismatches = (
            {
                "game": "tft",
                "puuid": "target-puuid",
                "region": "jp1",
            },
            {
                "game": "lol",
                "puuid": "different-puuid",
                "region": "jp1",
            },
        )

        for active_region in mismatches:
            with self.subTest(active_region=active_region):
                self.riot_api_client.reset_mock()
                self.riot_api_client.get_account_by_riot_id.return_value = {
                    "puuid": "target-puuid",
                }
                self.riot_api_client.get_active_region.return_value = (
                    active_region
                )

                with self.assertRaises(RegionResponseMismatchError):
                    self.service.search("TestPlayer", "TEST")

                self.riot_api_client.get_match_ids_by_puuid.assert_not_called()

    def test_rate_limit_or_timeout_stops_match_request(self):
        errors = (RiotRateLimitError(), RiotTimeoutError())

        for error in errors:
            with self.subTest(error=type(error).__name__):
                self.riot_api_client.reset_mock()
                self.riot_api_client.get_account_by_riot_id.return_value = {
                    "puuid": "target-puuid",
                }
                self.riot_api_client.get_active_region.side_effect = error

                with self.assertRaises(type(error)):
                    self.service.search("TestPlayer", "TEST")

                self.riot_api_client.get_match_ids_by_puuid.assert_not_called()

    def test_non_solo_duo_match_is_rejected(self):
        self.riot_api_client.get_match_detail.return_value = (
            build_match_detail(queue_id=400)
        )

        with self.assertRaises(UnexpectedQueueError):
            self.service.search("TestPlayer", "JP1")

    def test_missing_target_participant_is_rejected(self):
        self.riot_api_client.get_match_detail.return_value = (
            build_match_detail(puuid="other-puuid")
        )

        with self.assertRaises(ParticipantNotFoundError):
            self.service.search("TestPlayer", "JP1")

    def test_invalid_match_or_participant_data_is_rejected(self):
        invalid_details = (
            {},
            {"info": {"queueId": "420", "participants": []}},
            {"info": {"queueId": 420, "participants": "invalid"}},
            build_match_detail(champion_name=""),
            build_match_detail(win="true"),
            build_match_detail(kills=-1),
            build_match_detail(deaths=True),
            build_match_detail(assists=None),
        )

        for match_detail in invalid_details:
            with self.subTest(match_detail=match_detail):
                self.riot_api_client.get_match_detail.return_value = (
                    match_detail
                )

                with self.assertRaises(RiotInvalidResponseError):
                    self.service.search("TestPlayer", "JP1")


class RiotApiClientTest(unittest.TestCase):
    def test_missing_api_key_stops_before_http_request(self):
        session = Mock()
        client = RiotApiClient(
            api_key="   ",
            regional_route="asia",
            session=session,
        )

        with self.assertRaises(RiotConfigurationError):
            client.get_account_by_riot_id("TestPlayer", "JP1")

        session.get.assert_not_called()

    def test_client_uses_encoded_paths_query_params_and_auth_header(self):
        session = Mock()
        response = Mock(status_code=200)
        response.json.side_effect = [
            {"puuid": "test/puuid"},
            {"game": "lol", "puuid": "test/puuid", "region": "jp1"},
            ["JP1/test-match-id"],
            {"info": {"participants": []}},
        ]
        response.headers = {}
        session.get.return_value = response
        client = RiotApiClient(
            api_key="test-secret-api-key",
            regional_route="asia",
            session=session,
        )

        client.get_account_by_riot_id("Test Player/One", "JP#1")
        client.get_active_region("test/puuid")
        client.get_match_ids_by_puuid(
            "test/puuid",
            queue=420,
            start=0,
            count=1,
        )
        client.get_match_detail("JP1/test-match-id")

        headers = {"X-Riot-Token": "test-secret-api-key"}
        request_options = {
            "headers": headers,
            "timeout": (3.05, 10.0),
        }
        self.assertEqual(
            session.get.call_args_list,
            [
                call(
                    "https://asia.api.riotgames.com/riot/account/v1/"
                    "accounts/by-riot-id/Test%20Player%2FOne/JP%231",
                    **request_options,
                ),
                call(
                    "https://asia.api.riotgames.com/riot/account/v1/"
                    "region/by-game/lol/by-puuid/test%2Fpuuid",
                    **request_options,
                ),
                call(
                    "https://asia.api.riotgames.com/lol/match/v5/"
                    "matches/by-puuid/test%2Fpuuid/ids",
                    params={"queue": 420, "start": 0, "count": 1},
                    **request_options,
                ),
                call(
                    "https://asia.api.riotgames.com/lol/match/v5/"
                    "matches/JP1%2Ftest-match-id",
                    **request_options,
                ),
            ],
        )

    def test_http_errors_are_classified_without_retry(self):
        cases = (
            (401, RiotUnauthorizedError),
            (403, RiotForbiddenError),
            (404, RiotNotFoundError),
            (429, RiotRateLimitError),
            (500, RiotUnavailableError),
            (503, RiotUnavailableError),
        )

        for status_code, expected_error in cases:
            with self.subTest(status_code=status_code):
                session = Mock()
                response = Mock(status_code=status_code)
                response.headers = {"Retry-After": "15"}
                session.get.return_value = response
                client = RiotApiClient(
                    api_key="test-secret-api-key",
                    regional_route="asia",
                    session=session,
                )

                with self.assertRaises(expected_error) as context:
                    client.get_active_region("test-puuid")

                session.get.assert_called_once()
                if status_code == 429:
                    self.assertEqual(context.exception.retry_after, "15")

    def test_timeout_is_classified_without_retry(self):
        session = Mock()
        session.get.side_effect = requests.Timeout()
        client = RiotApiClient(
            api_key="test-secret-api-key",
            regional_route="asia",
            session=session,
        )

        with self.assertRaises(RiotTimeoutError):
            client.get_active_region("test-puuid")

        session.get.assert_called_once()

    def test_network_error_is_classified_without_retry(self):
        session = Mock()
        session.get.side_effect = requests.ConnectionError()
        client = RiotApiClient(
            api_key="test-secret-api-key",
            regional_route="asia",
            session=session,
        )

        with self.assertRaises(RiotUnavailableError):
            client.get_active_region("test-puuid")

        session.get.assert_called_once()

    def test_invalid_json_or_missing_fields_is_rejected(self):
        invalid_responses = (
            ValueError("invalid json"),
            {"game": "lol", "region": "jp1"},
        )

        for invalid_response in invalid_responses:
            with self.subTest(invalid_response=type(invalid_response).__name__):
                session = Mock()
                response = Mock(status_code=200)
                response.headers = {}
                if isinstance(invalid_response, Exception):
                    response.json.side_effect = invalid_response
                else:
                    response.json.return_value = invalid_response
                session.get.return_value = response
                client = RiotApiClient(
                    api_key="test-secret-api-key",
                    regional_route="asia",
                    session=session,
                )

                with self.assertRaises(RiotInvalidResponseError):
                    client.get_active_region("test-puuid")

                session.get.assert_called_once()


if __name__ == "__main__":
    unittest.main()
