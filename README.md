# Hotel Review Sentiment Analyzer

This project is a web application built with Flask that allows users to input a hotel name and view sentiment analysis of its reviews. The app uses Google Places API to fetch hotel reviews and OpenAI for aspect based sentiment analysis. It also integrates with SerpAPI to retrieve additional review data.

The current version of the project is always in `app.py`, while the repo might contain past iterations of the project in other files (for example, see the BERT implementation in `app_bert.py`).

This project is used as a continuous learning grounds for myself into sentiment analysis, LLMs and more advanced, production ready systems. Stay tuned!

## Features

- **Fetch hotel reviews**: Get reviews for a given hotel using Google Places API and SerpAPI.
- **Sentiment analysis**: Analyze the sentiment of reviews using LLMs to deduce aspect based sentiment analysis (service, cleanliness, location etc.).
- **Display results**: Present sentiment statistics and hotel details (name, rating, and total review count).

## Requirements

- Python 3.7+
- Google Places API key
- [Serp API key](https://serpapi.com/)

## Installation

1. Create a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up your API keys:

    Create a `.env` file in the root directory of the project and add your API keys:

    ```plaintext
    PLACES_API_KEY=your_api_key
    SERP_API_KEY=your_api_key
    OPEN_AI_API_KEY=your_api_key
    ```

## Running the Project

1. Start the Flask interface:

    ```bash
    python app.py
    ```

2. Open your web browser and navigate to the URL provided by Flask (usually `http://127.0.0.1:5000`).