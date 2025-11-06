from flask import request, jsonify
from datetime import datetime
import requests

class NewsController:
    def __init__(self, model_handler, news_api_key):
        self.model_handler = model_handler
        self.news_api_key = news_api_key

    def analyze_text(self):
        try:
            data = request.get_json()
            text = data.get("text", "").strip()
            if len(text) < 10:
                return jsonify({"error": "Text too short"}), 400
            fake = self.model_handler.predict_fake_news(text)
            ai = self.model_handler.predict_ai_generated(text)
            return jsonify({
                "fakeNews": fake,
                "aiGenerated": ai,
                "metadata": {
                    "wordCount": len(text.split()),
                    "analysisTime": fake["analysis_time"] + ai["analysis_time"],
                    "timestamp": datetime.now().isoformat()
                }
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def analyze_url(self):
        try:
            data = request.get_json()
            url = data.get("url", "")
            if not url:
                return jsonify({"error": "No URL provided"}), 400
            text = self.model_handler.extract_text_from_url(url)
            if not text:
                return jsonify({"error": "Failed to extract text"}), 400
            fake = self.model_handler.predict_fake_news(text)
            ai = self.model_handler.predict_ai_generated(text)
            return jsonify({
                "fakeNews": fake,
                "aiGenerated": ai,
                "metadata": {
                    "wordCount": len(text.split()),
                    "analysisTime": fake["analysis_time"] + ai["analysis_time"],
                    "timestamp": datetime.now().isoformat(),
                    "sourceUrl": url
                }
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def fetch_latest_news(self, topic):
        try:
            url = f"https://newsapi.org/v2/top-headlines?q={topic}&language=en&apiKey={self.news_api_key}"
            response = requests.get(url)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
