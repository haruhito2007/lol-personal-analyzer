from flask import Flask, render_template, request, jsonify
import os 
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.getenv("RIOT_API_KEY")

print(api_key is not None)

app = Flask(__name__)

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
  data = request.get_json()

  game_name = data["gameName"]
  tagline = data["tagline"]

  print(game_name)
  print(tagline)

  url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tagline}"

  headers = {
    "X-Riot-Token": api_key
  }

  response = requests.get(url, headers=headers)

  riot_data = response.json()
  puuid = riot_data["puuid"]
  print(puuid)

  match_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
  match_response = requests.get(match_url, headers=headers)

  # print(match_response.status_code)
  # print(match_response.json())

  match_ids = match_response.json()
  latest_match_id = match_ids[0]
  print(latest_match_id) 

  detail_url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{latest_match_id}"
  detail_response = requests.get(detail_url, headers=headers)

  detail_data = detail_response.json()

  print(detail_response.status_code)
  print(detail_data.keys())

  participants = detail_data["info"]["participants"]

  for participant in participants:
    if participant["puuid"] == puuid:
      print(participant["championName"])

  return jsonify({
    "gameName": game_name,
    "tagline": tagline
  })

if __name__ == "__main__":
  app.run(debug=True)