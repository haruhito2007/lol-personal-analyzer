from summoners_note.errors import (
    InvalidRiotIdError,
    ParticipantNotFoundError,
    PlayerNotFoundError,
    RegionLookupNotFoundError,
    RegionResponseMismatchError,
    RegionUnconfirmedError,
    RiotInvalidResponseError,
    RiotNotFoundError,
    UnexpectedQueueError,
)


class PlayerSearchService:
    LOL_GAME = "lol"
    CONFIRMED_JP1_REGION = "jp1"
    SOLO_DUO_QUEUE = 420
    FIRST_MATCH_INDEX = 0
    LATEST_MATCH_COUNT = 1

    def __init__(self, riot_api_client):
        self._riot_api_client = riot_api_client

    def search(self, game_name, tagline):
        game_name, tagline = self._validate_riot_id(game_name, tagline)

        try:
            account = self._riot_api_client.get_account_by_riot_id(
                game_name,
                tagline,
            )
        except RiotNotFoundError as error:
            raise PlayerNotFoundError() from error

        puuid = account["puuid"]

        try:
            active_region = self._riot_api_client.get_active_region(puuid)
        except RiotNotFoundError as error:
            raise RegionLookupNotFoundError() from error

        self._confirm_jp1(active_region, puuid)

        match_ids = self._riot_api_client.get_match_ids_by_puuid(
            puuid,
            queue=self.SOLO_DUO_QUEUE,
            start=self.FIRST_MATCH_INDEX,
            count=self.LATEST_MATCH_COUNT,
        )

        if not match_ids:
            return self._build_result(game_name, tagline, latest_match=None)

        latest_match_id = match_ids[0]
        match_detail = self._riot_api_client.get_match_detail(latest_match_id)
        latest_match = self._extract_latest_match(match_detail, puuid)

        return self._build_result(game_name, tagline, latest_match)

    def _confirm_jp1(self, active_region, expected_puuid):
        if (
            active_region["game"] != self.LOL_GAME
            or active_region["puuid"] != expected_puuid
        ):
            raise RegionResponseMismatchError()

        if active_region["region"] != self.CONFIRMED_JP1_REGION:
            raise RegionUnconfirmedError()

    @staticmethod
    def _validate_riot_id(game_name, tagline):
        if not isinstance(game_name, str) or not isinstance(tagline, str):
            raise InvalidRiotIdError()

        game_name = game_name.strip()
        tagline = tagline.strip()

        if (
            not game_name
            or not tagline
            or not game_name.isprintable()
            or not tagline.isprintable()
        ):
            raise InvalidRiotIdError()

        return game_name, tagline

    def _extract_latest_match(self, match_detail, puuid):
        info = match_detail.get("info")
        if not isinstance(info, dict):
            raise RiotInvalidResponseError()

        queue_id = info.get("queueId")
        if not self._is_integer(queue_id):
            raise RiotInvalidResponseError()
        if queue_id != self.SOLO_DUO_QUEUE:
            raise UnexpectedQueueError()

        participants = info.get("participants")
        if not isinstance(participants, list):
            raise RiotInvalidResponseError()

        participant = next(
            (
                candidate
                for candidate in participants
                if isinstance(candidate, dict)
                and candidate.get("puuid") == puuid
            ),
            None,
        )
        if participant is None:
            raise ParticipantNotFoundError()

        return self._build_match_data(participant)

    def _build_match_data(self, participant):
        champion_name = participant.get("championName")
        win = participant.get("win")
        kills = participant.get("kills")
        deaths = participant.get("deaths")
        assists = participant.get("assists")

        if not isinstance(champion_name, str) or not champion_name:
            raise RiotInvalidResponseError()
        if not isinstance(win, bool):
            raise RiotInvalidResponseError()
        if not all(
            self._is_nonnegative_integer(value)
            for value in (kills, deaths, assists)
        ):
            raise RiotInvalidResponseError()

        zero_deaths = deaths == 0
        if zero_deaths:
            kda = float(kills + assists)
        else:
            kda = (kills + assists) / deaths

        return {
            "championName": champion_name,
            "win": win,
            "kills": kills,
            "deaths": deaths,
            "assists": assists,
            "kda": kda,
            "zeroDeaths": zero_deaths,
        }

    @staticmethod
    def _build_result(game_name, tagline, latest_match):
        return {
            "gameName": game_name,
            "tagline": tagline,
            "latestMatch": latest_match,
        }

    @staticmethod
    def _is_integer(value):
        return isinstance(value, int) and not isinstance(value, bool)

    @classmethod
    def _is_nonnegative_integer(cls, value):
        return cls._is_integer(value) and value >= 0
