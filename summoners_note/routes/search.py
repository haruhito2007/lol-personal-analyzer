from flask import Blueprint, current_app, jsonify, render_template, request

from summoners_note.errors import InvalidRiotIdError


search_blueprint = Blueprint("search", __name__)


@search_blueprint.get("/")
def index():
    return render_template("index.html")


@search_blueprint.post("/search")
def search():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise InvalidRiotIdError()

    game_name = data.get("gameName")
    tagline = data.get("tagline")

    service = current_app.extensions["player_search_service"]
    result = service.search(game_name, tagline)

    return jsonify(result)
