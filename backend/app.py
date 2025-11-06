from core.app_config import AppConfig
from services.model_handler import ModelHandler
from controllers.news_controller import NewsController
from controllers.twitter_controller import TwitterController
from dotenv import load_dotenv
from flask import jsonify, request
import os
import logging
from datetime import datetime

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = AppConfig()
app, socketio = config.get_app()

model_handler = ModelHandler()
news_controller = NewsController(model_handler, os.getenv("NEWS_API_KEY"))
twitter_controller = TwitterController(socketio, model_handler, os.getenv("X_BEARER_TOKEN"))

@app.route('/')
def home():
    return " Flask OOP Backend Running with Real-Time Tracking"

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': model_handler.models_loaded
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    try:
        return news_controller.analyze_text()
    except Exception as e:
        logger.error(f"Error in /api/analyze: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-url', methods=['POST'])
def analyze_url():
    try:
        return news_controller.analyze_url()
    except Exception as e:
        logger.error(f"Error in /api/analyze-url: {e}")
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def on_connect():
    logger.info("Client connected to Socket.IO")
    socketio.emit('server_message', {'message': 'Connected to Flask News Tracker'})

@socketio.on('track_news')
def on_track_news(data):
    try:
        topic = (data or {}).get('topic', 'technology')
        logger.info(f"Tracking live news for topic: {topic}")
        news_data = news_controller.fetch_latest_news(topic)
        if news_data.get("status") == "ok":
            for article in news_data.get("articles", [])[:5]:
                socketio.emit('news_update', {
                    'headline': article.get('title'),
                    'source': article.get('source', {}).get('name'),
                    'url': article.get('url'),
                    'timestamp': article.get('publishedAt')
                })
        else:
            socketio.emit('news_error', {'message': 'No articles found'})
    except Exception as e:
        logger.error(f"Error in track_news: {e}")
        socketio.emit('news_error', {'message': str(e)})

@socketio.on('track_twitter')
def on_track_twitter(data):
    try:
        topic = (data or {}).get('topic', 'India')
        logger.info(f"Starting Twitter stream for topic: {topic}")
        twitter_controller.start_stream([topic])
        socketio.emit('server_message', {'message': f"Tracking live tweets for '{topic}'"})
    except Exception as e:
        logger.error(f"Error in track_twitter: {e}")
        socketio.emit('news_error', {'message': str(e)})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
