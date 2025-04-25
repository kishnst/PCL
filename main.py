import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import google.generativeai as genai
from logger_config import logger

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Initialize NewsAPI client
try:
    newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
    if not os.getenv('NEWS_API_KEY'):
        logger.error("NEWS_API_KEY not found in environment variables")
except Exception as e:
    logger.error(f"Error initializing NewsAPI client: {str(e)}")

# Initialize Gemini API
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    if not os.getenv('GEMINI_API_KEY'):
        logger.error("GEMINI_API_KEY not found in environment variables")
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    logger.error(f"Error initializing Gemini API: {str(e)}")

# Predefined topics with their search queries
TOPICS = {
    'technology': 'technology OR AI OR artificial intelligence OR software OR hardware',
    'business': 'business OR economy OR market OR finance OR stocks',
    'politics': 'politics OR government OR election OR policy',
    'sports': 'sports OR football OR basketball OR soccer OR tennis',
    'entertainment': 'entertainment OR movies OR music OR celebrities',
    'science': 'science OR research OR discovery OR space OR medicine',
    'health': 'health OR medical OR healthcare OR wellness',
    'environment': 'environment OR climate OR nature OR conservation'
}

def get_sentiment_label(compound_score):
    """Return a human-readable sentiment label based on the compound score."""
    if compound_score >= 0.05:
        return "Positive"
    elif compound_score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def analyze_news(topic='technology'):
    """Fetch and analyze sentiment of recent news articles."""
    try:
        # Get yesterday's date
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')

        # Get the search query for the selected topic
        search_query = TOPICS.get(topic, TOPICS['technology'])
        logger.info(f"Fetching news for topic: {topic}")

        # Fetch news articles with the selected topic
        articles = newsapi.get_everything(
            q=search_query,
            language='en',
            from_param=yesterday_str,
            sort_by='publishedAt',
            page_size=10
        )

        # Process articles
        processed_articles = []
        for article in articles['articles']:
            title = article['title']
            source = article['source']['name']
            url = article['url']
            description = article.get('description', '')
            
            # Perform sentiment analysis
            sentiment_scores = analyzer.polarity_scores(title)
            compound_score = sentiment_scores['compound']
            sentiment_label = get_sentiment_label(compound_score)
            
            processed_articles.append({
                'title': title,
                'source': source,
                'url': url,
                'description': description,
                'sentiment': sentiment_label,
                'compound_score': compound_score
            })

        logger.info(f"Successfully processed {len(processed_articles)} articles")
        return processed_articles
        
    except Exception as e:
        logger.error(f"Error in analyze_news: {str(e)}")
        return []

def get_chat_response(message):
    """Get a response from Gemini API based on the user message."""
    try:
        # Create a prompt that includes context about the news analyzer
        prompt = f"""You are a helpful news assistant that can analyze and discuss news articles. 
The user is using a news sentiment analyzer that shows sentiment scores for articles.

User Question: {message}

Please provide a helpful, informative response that:
1. Directly addresses the user's question
2. Maintains a professional and engaging tone
3. Is concise and clear
4. If the question is about sentiment analysis, explain how it works

Your response:"""

        # Generate response using Gemini with safety settings
        response = model.generate_content(
            prompt,
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
        )
        
        # Check if the response is valid
        if response and hasattr(response, 'text'):
            return response.text
        else:
            logger.error("Invalid response from Gemini API")
            return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
            
    except Exception as e:
        logger.error(f"Error in get_chat_response: {str(e)}")
        return "I apologize, but I'm having trouble processing your request at the moment. Please try again."

@app.route('/')
def index():
    """Render the main page."""
    try:
        return render_template('index.html', topics=TOPICS)
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return "Error loading page", 500

@app.route('/get_news')
def get_news():
    """API endpoint to get news articles with sentiment analysis."""
    try:
        topic = request.args.get('topic', 'technology')
        articles = analyze_news(topic)
        return jsonify({'articles': articles})
    except Exception as e:
        logger.error(f"Error in get_news endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """API endpoint for chat interactions."""
    try:
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({'error': 'Missing message'}), 400
        
        response = get_chat_response(message)
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == "__main__":
    # Check if required environment variables are set
    if not os.getenv('NEWS_API_KEY'):
        logger.error("NEWS_API_KEY not found in environment variables")
    if not os.getenv('GEMINI_API_KEY'):
        logger.error("GEMINI_API_KEY not found in environment variables")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
