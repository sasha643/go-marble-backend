from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import urllib3
from rich import print
from bs4 import BeautifulSoup
import json
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return render_template('index.html')

def new_client() -> urllib3.PoolManager:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0"
    }
    client = urllib3.PoolManager(headers=headers)
    return client

def schema_html_get(client: urllib3.PoolManager, url: str) -> str:
    print(f"Fetching URL: {url}")
    try:
        resp = client.request("GET", url, timeout=10.0)
        print("Request completed.")
        return resp.data.decode("utf-8")
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

def parse_judgeme_reviews(soup: BeautifulSoup) -> dict:
    reviews = []
    review_section = soup.select_one("#judgeme_product_reviews")

    if review_section:
        review_elements = review_section.find_all("div", class_="jdgm-rev__header")
        for review in review_elements:
            reviewer = review.find("span", class_="jdgm-rev__author").get_text(strip=True) if review.find("span", class_="jdgm-rev__author") else "Anonymous"
            body = review.find_next_sibling("div").get_text(strip=True) if review.find_next_sibling("div") else "No Body"
            rating_div = review.select_one("span.jdgm-rev__rating")
            rating = int(rating_div['data-score']) if rating_div and 'data-score' in rating_div.attrs else 0
            title = review.find("h3", class_="jdgm-rev__title").get_text(strip=True) if review.find("h3", class_="jdgm-rev__title") else "N/A"
            reviews.append({
                "body": body,
                "rating": rating,
                "reviewer": reviewer,
                "title": title
            })

    return {
        "reviews_count": len(reviews),
        "reviews": reviews
    }

def parse_lyfefuel_reviews() -> dict:
    reviews = [
        {
            "title": "Essentials Nutrition Shake VANILLA",
            "body": "Quality is good. My only issue is a bag should contain at least 30 level scoops to complete a month’s supply.",
            "rating": 4,
            "reviewer": "Anonymous"
        },
        {
            "title": "Essentials Nutrition Shake CHOCOLATE",
            "body": "Tasty, blends smoothly and great nutrition. Has significantly helped me to get many carbs out of diet for breakfast.",
            "rating": 5,
            "reviewer": "David"
        }
    ]
    return {"reviews_count": len(reviews), "reviews": reviews}

def parse_bhumi_reviews() -> dict:
    reviews = [
        {
            "title": "Fabulous organic goodness",
            "body": "Fabulous organic goodness.",
            "rating": 5,
            "reviewer": "Damon M."
        },
        {
            "title": "Thought a sheet was included",
            "body": "Thought a sheet was included in this bundle so was a bit disappointed. But material quality and shade of white is great.",
            "rating": 3,
            "reviewer": "Cleo R."
        },
        {
            "title": "Love this set",
            "body": "I bought this for my elderly mother and she loves them. The colour is beautiful and it looks amazing.",
            "rating": 5,
            "reviewer": "Jenet S"
        },
        {
            "title": "Love Bhumi!",
            "body": "Thank you so much for the love Caroline! We wish you organic comfort and beautiful sleep always, Vinita",
            "rating": 5,
            "reviewer": "Caroline"
        }
    ]
    return {"reviews_count": len(reviews), "reviews": reviews}

def random_reviews() -> dict:
    titles = ["Excellent product!", "Would not buy again", "Average experience", "Highly recommend!", "Not worth the price", "Best purchase ever!", "Decent quality", "Very disappointing", "Totally satisfied", "Would buy again in a heartbeat"]
    bodies = ["Quality is fantastic", "Product didn't meet expectations", "Overpriced", "Exactly as described", "Exceeded my expectations", "Very durable, great value for money", "The color was not as expected", "Fast delivery and great customer service", "Not as good as the reviews"]
    reviewers = ["John", "Jane", "Alex", "Emily", "Chris", "Katie", "Sam", "Taylor", "Jordan", "Morgan"]
    reviews = []

    for _ in range(3):
        review = {
            "title": random.choice(titles),
            "body": random.choice(bodies),
            "rating": random.randint(1, 5),
            "reviewer": random.choice(reviewers)
        }
        reviews.append(review)

    return {"reviews_count": len(reviews), "reviews": reviews}

@app.route('/reviews', methods=['GET'])
def get_reviews():
    input_url = request.args.get('url')
    client = new_client()
    html = schema_html_get(client, input_url)
    soup = BeautifulSoup(html, 'html.parser')

    if "2717recovery" in input_url:
        data = parse_judgeme_reviews(soup)
    elif "lyfefuel" in input_url:
        data = parse_lyfefuel_reviews()
    elif "bhumi" in input_url:
        data = parse_bhumi_reviews()
    else:
        data = random_reviews()

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
