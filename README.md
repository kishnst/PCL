# News Sentiment Analyzer

This application performs real-time sentiment analysis on news articles using VADER (Valence Aware Dictionary and sEntiment Reasoner).

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory with your NewsAPI key:
```
NEWS_API_KEY=your_api_key_here
```

You can get a NewsAPI key by signing up at: https://newsapi.org/

## Usage

Run the application using:
```bash
python main.py
```

The application will fetch recent news articles and display their sentiment analysis results, including:
- Positive, Negative, and Neutral scores
- Compound sentiment score
- Article title and source
- Brief summary of the sentiment

## Sentiment Score Interpretation

The compound score is a unified score between -1 (most negative) and +1 (most positive):
- score >= 0.05: Positive sentiment
- -0.05 < score < 0.05: Neutral sentiment
- score <= -0.05: Negative sentiment 