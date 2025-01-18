from flask import Flask, render_template, request
import requests
from textblob import TextBlob 
import os
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

PLACES_API_KEY=os.getenv('PLACES_API_KEY')
SERP_API_KEY=os.getenv('SERP_API_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        hotel_name = request.form['hotel_name']
        # Fetch hotel reviews from Google Places API
        reviews, hotel_details = get_reviews(hotel_name)
        sentiment_results = analyze_sentiment(reviews)
        return render_template('index.html', sentiment_results=sentiment_results, hotel_details=hotel_details)
    return render_template('index.html', sentiment_results=None, hotel_details=None)

def get_reviews(hotel_name):
    search_url =  f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={hotel_name}&key={PLACES_API_KEY}'
    search_response = requests.get(search_url)
    search_data = search_response.json()

    # Get the place ID of the first hotel in the search results
    first_found_hotel = search_data['results'][0]

    hotel_details = {
        'place_id': first_found_hotel['place_id'],
        'hotel_full_name': first_found_hotel['name'],
        'rating': first_found_hotel['rating']
    }

    # Fetch place details and reviews using the place ID and SerpAPI
    # It uses pagination - for now, we will just get the results on the first 3 pages
    params = {
        'engine': 'google_maps_reviews',
        'hl': 'en',
        'place_id': hotel_details['place_id'],
        'next_page_token': '',
        'api_key': SERP_API_KEY
    }

    reviews = []

    # The SerpAPI has limited API calls you can do for free. Since this is a dev project, this is a smaller amount to account for that
    for i in range(3): 
        search = GoogleSearch(params)
        results = search.get_dict()
        reviews.extend(results["reviews"])
        print(len(reviews))
        params['next_page_token'] = results['serpapi_pagination']['next_page_token']
        params['num'] = 20

    hotel_details['total_review_count'] = len(reviews)
    return reviews, hotel_details

def analyze_sentiment(reviews):
    sentiment_counts = {
        'positive': 0,
        'neutral': 0,
        'negative': 0
    }

    for review in reviews:
        text = review['snippet']
        sentiment = TextBlob(text).sentiment.polarity

        if sentiment > 0:
            sentiment_counts['positive'] += 1
        elif sentiment == 0:
            sentiment_counts['neutral'] += 1
        else:
            sentiment_counts['negative'] += 1

    # Calculate percentages
    reviews_count = len(reviews)
    if reviews_count > 0:
        sentiment_counts = { key: (count / reviews_count) *100 for key, count in sentiment_counts.items()}
    return sentiment_counts

if __name__ == '__main__':
    app.run(debug=True)
