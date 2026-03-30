import json
import os

import requests
from dotenv import load_dotenv
from django.http import HttpResponse, HttpResponseBadRequest
from requests.auth import HTTPBasicAuth
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .models import CarDealer, CarReview


load_dotenv()

CF_API_KEY = os.getenv("CF_API_KEY")
sentiment_analyzer = SentimentIntensityAnalyzer()


def get_request(url, auth=None, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        request_kwargs = {
            "headers": {"Content-Type": "application/json"},
            "params": kwargs,
        }
        if CF_API_KEY:
            request_kwargs["auth"] = HTTPBasicAuth("apikey", CF_API_KEY)
        response = requests.get(url, **request_kwargs)
    except Exception as error:
        print(f"Network exception occurred: {error}")
        return None

    print("With status {} ".format(response.status_code))
    try:
        json_data = response.json()
    except ValueError:
        print("Response did not contain valid JSON")
        return None

    if response.status_code >= 400:
        print(f"Request returned error payload: {json_data}")
        return None

    return json_data


def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url, **kwargs)
    dealer_documents = []
    if isinstance(json_result, list):
        for dealer_doc in json_result:
            if isinstance(dealer_doc, dict) and isinstance(dealer_doc.get("dealerships"), list):
                dealer_documents.extend(dealer_doc["dealerships"])
            else:
                dealer_documents.append(dealer_doc)
    elif isinstance(json_result, dict) and isinstance(json_result.get("dealerships"), list):
        dealer_documents = json_result["dealerships"]

    if dealer_documents:
        for dealer_doc in dealer_documents:
            if not isinstance(dealer_doc, dict):
                print(f"Skipping unexpected dealer payload: {dealer_doc}")
                continue
            print("Dealer", dealer_doc)
            dealer_obj = CarDealer(
                address=dealer_doc["address"],
                city=dealer_doc["city"],
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"],
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                st=dealer_doc["st"],
                zip=dealer_doc["zip"],
                state=dealer_doc["state"],
            )
            results.append(dealer_obj)
    elif json_result is not None:
        print(f"Unexpected dealers response shape: {json_result}")

    return results


def get_reviews_from_cf(url, **kwargs):
    results = []
    keylist = [
        "dealership",
        "name",
        "time",
        "id",
        "review",
        "purchase",
        "purchase_date",
        "car_make",
        "car_model",
        "car_year",
    ]
    try:
        json_result = get_request(url, **kwargs)
        review_documents = []
        if isinstance(json_result, list):
            for review in json_result:
                if isinstance(review, dict) and isinstance(review.get("reviews"), list):
                    review_documents.extend(review["reviews"])
                else:
                    review_documents.append(review)
        elif isinstance(json_result, dict) and isinstance(json_result.get("reviews"), list):
            review_documents = json_result["reviews"]

        if review_documents:
            for review in review_documents:
                if not isinstance(review, dict):
                    print(f"Skipping unexpected review payload: {review}")
                    continue
                for key in keylist:
                    if key not in review:
                        review[key] = ""

                print("Review", review)
                review_new = CarReview(
                    dealership=review["dealership"],
                    name=review["name"],
                    id=review["id"],
                    review=review["review"],
                    purchase=review["purchase"],
                    purchase_date=review["purchase_date"],
                    car_make=review["car_make"],
                    car_model=review["car_model"],
                    car_year=review["car_year"],
                    time=review["time"],
                    sentiment=analyze_review_sentiments(review["review"]),
                )
                print(review["review"])
                results.append(review_new)
            return results
        # if json_result is not None:
        #     print(f"Unexpected reviews response shape: {json_result}")
        #     return []
    except Exception:
        return None


def post_request(url, data):
    required_fields = ["id", "name", "dealership", "review"]

    try:
        datajson = json.loads(data)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON data")

    if not datajson:
        return HttpResponseBadRequest("JSON data missing")

    for field in required_fields:
        if field not in datajson:
            return HttpResponseBadRequest(f"{field} is a required field, and it is missing")

    try:
        response = requests.post(url, json=datajson)
        response.raise_for_status()
    except requests.RequestException as error:
        return HttpResponse(f"Failed to post review: {error}", status=500)

    return HttpResponse("Review posted successfully")


def analyze_review_sentiments(dealerreview):
    if not dealerreview:
        return "neutral"

    sentiment_scores = sentiment_analyzer.polarity_scores(dealerreview)
    compound_score = sentiment_scores["compound"]

    if compound_score >= 0.05:
        return "positive"
    if compound_score <= -0.05:
        return "negative"
    return "neutral"
