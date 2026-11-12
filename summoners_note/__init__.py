from pathlib import Path

from flask import Flask

from summoners_note.clients.riot_api import RiotApiClient
from summoners_note.config import Config
from summoners_note.errors import register_error_handlers
from summoners_note.routes.search import search_blueprint
from summoners_note.services.player_search import PlayerSearchService


def create_app(test_config=None, *, riot_api_client=None):
    """Create and configure the Flask application."""
    project_root = Path(__file__).resolve().parent.parent

    app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    if riot_api_client is None:
        riot_api_client = RiotApiClient(
            api_key=app.config["RIOT_API_KEY"],
            regional_route=app.config["RIOT_REGIONAL_ROUTE"],
            timeout=app.config["RIOT_API_TIMEOUT"],
        )

    client = riot_api_client
    app.extensions["player_search_service"] = PlayerSearchService(client)
    app.register_blueprint(search_blueprint)
    register_error_handlers(app)

    return app
