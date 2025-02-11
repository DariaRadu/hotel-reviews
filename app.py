from flask import Flask, render_template, request
import requests
import os
from serpapi import GoogleSearch
from dotenv import load_dotenv
from openai import AsyncOpenAI
import asyncio
import nest_asyncio
import json

load_dotenv()
nest_asyncio.apply()

app = Flask(__name__)

PLACES_API_KEY=os.getenv('PLACES_API_KEY')
SERP_API_KEY=os.getenv('SERP_API_KEY')

client = AsyncOpenAI(
  api_key=os.environ['OPEN_AI_API_KEY']
)

@app.route('/', methods=['GET', 'POST'])
async def index():
    if request.method == 'POST':
        hotel_name = request.form['hotel_name']
        # Fetch hotel reviews from Google Places API
        reviews, hotel_details = get_reviews(hotel_name)
        sentiment_results = await analyse_all_review_sentiments(reviews)
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
        params['next_page_token'] = results['serpapi_pagination']['next_page_token']
        params['num'] = 20

    hotel_details['total_review_count'] = len(reviews)
    return reviews, hotel_details

async def analyse_all_review_sentiments(reviews):
    sentiment_aspects = {
        'service': 0,
        'cleanliness': 0,
        'location': 0,
        'amenities': 0,
        'value_for_money': 0
    }

    review_snippets = [review['snippet'] for review in reviews]
    tasks = [analyze_sentiment_aspect_based(review) for review in review_snippets]
    aspect_based_review_results = await asyncio.gather(*tasks)

    for result in aspect_based_review_results:
        result_json = json.loads(result)
        for aspect in sentiment_aspects.keys():
            sentiment_aspects[aspect] += int(result_json[aspect]['sentiment'])

    print(sentiment_aspects)
    return sentiment_aspects

async def analyze_sentiment_aspect_based(review_text):
    prompt = f"""
        You are an expert in sentiment analysis for hotel reviews.
        Analyze the following review and classify sentiment for key aspects:
        
        - Service
        - Cleanliness
        - Location
        - Amenities
        - Value for Money

        Provide sentiment scores (-1 = Negative, 0 = Neutral, 1 = Positive) and a really short explanation.

        Review: "{review_text}"
        
        Respond directly in JSON format, which can be parsed easily:
        {{
            "service": {{"sentiment": ..., "explanation": "..."}},
            "cleanliness": {{"sentiment": ..., "explanation": "..."}},
            "location": {{"sentiment": ..., "explanation": "..."}},
            "amenities": {{"sentiment": ..., "explanation": "..."}},
            "value_for_money": {{"sentiment": ..., "explanation": "..."}}
        }}
    """

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={ "type": "json_object" },
        messages=[{"role": "system", "content": "You are an AI that performs Aspect-Based Sentiment Analysis."},
                {"role": "user", "content": prompt}],
        temperature=0  # Set to 0 for consistent output
    )

    result = response.choices[0].message.content
    return result

if __name__ == '__main__':
    app.run(debug=True)
