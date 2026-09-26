from flask import Flask, render_template, request, jsonify

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

  return jsonify({
    "gameName": game_name,
    "tagline": tagline
  })

if __name__ == "__main__":
  app.run(debug=True)