from flask import Flask, render_template, request, jsonify
import requests
import cachetools

app = Flask(__name__)
categorycache = cachetools.TTLCache(10, 1800)

@app.route("/")
def homepage():
	return render_template("index.html")

@app.route("/proxy")
def proxy():
	query = request.args.get("q")
	category = request.args.get("category")
	if not query or not category:
		return jsonify({})

	pages = categorycache.get(category, None)
	if not pages:
		params = {
			"action": "query",
			"generator": "categorymembers",
			"gcmtitle": f"Category:{category}",
			"gcmtype": "page",
			"gcmlimit": 500,
			"prop": "info",
			"inprop": "url",
			"formatversion": 2,
			"format": "json"
		}

		pages = []
		cmcontinue = None

		while True:
			if cmcontinue:
				params["gcmcontinue"] = cmcontinue

			res = requests.get("https://qwrky.dev/mediawiki/api.php", params=params)
			data = res.json()
			pages.extend(data["query"].get("pages", []))
			cmcontinue = data.get("continue", {}).get("gcmcontinue")
			if not cmcontinue:
				break

		categorycache[category] = pages

	titles = [(page["title"], page["fullurl"], page["touched"]) for page in pages if query.lower().strip() in page["title"].lower()]
	return jsonify(titles)

if __name__ == "__main__":
	app.run(debug=True)