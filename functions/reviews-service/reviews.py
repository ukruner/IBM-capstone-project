import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request
from pymongo import MongoClient
import certifi

load_dotenv(os.getenv("DOTENV_PATH") or Path(__file__).resolve().parents[2] / ".env")

def sanitize_mongo_uri(uri):
    if not uri:
        return uri

    split_uri = urlsplit(uri)
    query_pairs = parse_qsl(split_uri.query, keep_blank_values=True)
    app_names = [value for key, value in query_pairs if key == "appName"]
    if len(app_names) <= 1:
        return uri

    filtered_pairs = [(key, value) for key, value in query_pairs if key != "appName"]
    filtered_pairs.append(("appName", app_names[0]))
    return urlunsplit(
        (
            split_uri.scheme,
            split_uri.netloc,
            split_uri.path,
            urlencode(filtered_pairs),
            split_uri.fragment,
        )
    )


mongo_uri = sanitize_mongo_uri(os.getenv("MONGODB_URI"))
db_name = os.getenv("MONGODB_DB_NAME", "dealerships_db")
reviews_collection_name = os.getenv("MONGODB_REVIEWS_COLLECTION", "reviews")

if not mongo_uri:
    raise RuntimeError("Missing MongoDB configuration. Set MONGODB_URI in .env.")

client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
db = client[db_name]
reviews_collection = db[reviews_collection_name]

app = Flask(__name__)


@app.route("/api/review", methods=["GET"])
def get_reviews():
    dealership_id = request.args.get("id")

    if dealership_id is None:
        return jsonify({"error": "Missing 'id' parameter in the URL"}), 400

    try:
        dealership_id = int(dealership_id)
    except ValueError:
        return jsonify({"error": "'id' parameter must be an integer"}), 400

    cursor = reviews_collection.find(
        {"dealership": dealership_id},
        {"_id": 0},
    )
    data_list = list(cursor)
    return jsonify(data_list)


@app.route("/api/review", methods=["POST"])
def post_review():
    if not request.json:
        abort(400, description="Invalid JSON data")

    review_data = request.json
    required_fields = ["dealership", "review", "purchase", "purchase_date"]
    for field in required_fields:
        if field not in review_data:
            abort(400, description=f"Missing required field: {field}")

    reviews_collection.insert_one(review_data)
    return jsonify({"message": "Review posted successfully"}), 201


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Something went wrong on the server"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
