from flask import jsonify


class ApplicationError(Exception):
    code = "application_error"
    message = "処理を完了できませんでした。"
    status_code = 500

    def __init__(self, *, retry_after=None):
        super().__init__(self.message)
        self.retry_after = retry_after


class RiotApiError(ApplicationError):
    code = "riot_api_error"
    message = "Riot APIへの接続でエラーが発生しました。"
    status_code = 502


class RiotConfigurationError(RiotApiError):
    code = "riot_api_configuration_error"
    message = "Riot APIキーが設定されていません。"
    status_code = 503


class RiotUnauthorizedError(RiotApiError):
    code = "riot_api_unauthorized"
    message = "Riot APIの認証を確認できませんでした。"
    status_code = 503


class RiotForbiddenError(RiotApiError):
    code = "riot_api_forbidden"
    message = "Riot APIへのアクセスが拒否されました。"
    status_code = 503


class RiotNotFoundError(RiotApiError):
    code = "riot_data_not_found"
    message = "Riot APIで対象データを確認できませんでした。"
    status_code = 404


class RiotRateLimitError(RiotApiError):
    code = "riot_api_rate_limited"
    message = "Riot APIの利用上限に達しました。時間をおいて再度お試しください。"
    status_code = 429


class RiotTimeoutError(RiotApiError):
    code = "riot_api_timeout"
    message = "Riot APIから時間内に応答がありませんでした。"
    status_code = 504


class RiotUnavailableError(RiotApiError):
    code = "riot_api_unavailable"
    message = "Riot APIを一時的に利用できません。"
    status_code = 503


class RiotInvalidResponseError(RiotApiError):
    code = "riot_api_invalid_response"
    message = "Riot APIから必要なデータを取得できませんでした。"
    status_code = 502


class PlayerNotFoundError(ApplicationError):
    code = "player_not_found"
    message = "指定されたRiot IDのプレイヤーが見つかりませんでした。"
    status_code = 404


class RegionLookupNotFoundError(ApplicationError):
    code = "region_not_found"
    message = "プレイヤーの所属地域を確認できませんでした。"
    status_code = 422


class RegionUnconfirmedError(ApplicationError):
    code = "region_unconfirmed"
    message = "日本サーバー所属であることを確認できませんでした。"
    status_code = 422


class RegionResponseMismatchError(ApplicationError):
    code = "region_response_mismatch"
    message = "所属地域の確認結果が検索対象と一致しませんでした。"
    status_code = 422


class InvalidRiotIdError(ApplicationError):
    code = "invalid_riot_id"
    message = "ゲーム名とタグラインを正しく入力してください。"
    status_code = 400


class UnexpectedQueueError(ApplicationError):
    code = "unexpected_queue"
    message = "Solo/Duoランク以外の試合データは表示できません。"
    status_code = 502


class ParticipantNotFoundError(ApplicationError):
    code = "participant_not_found"
    message = "試合データから対象プレイヤーを確認できませんでした。"
    status_code = 502


def register_error_handlers(app):
    @app.errorhandler(ApplicationError)
    def handle_application_error(error):
        response = jsonify(
            {
                "error": {
                    "code": error.code,
                    "message": error.message,
                }
            }
        )
        response.status_code = error.status_code

        if error.retry_after:
            response.headers["Retry-After"] = error.retry_after

        return response
