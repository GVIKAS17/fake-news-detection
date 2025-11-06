import tweepy
import threading
from datetime import datetime
import logging

class TwitterController:
    def __init__(self, socketio, model_handler, bearer_token):
        self.socketio = socketio
        self.model_handler = model_handler
        self.bearer_token = bearer_token
        self.logger = logging.getLogger(__name__)

    class TweetStreamer(tweepy.StreamingClient):
        def __init__(self, bearer, socketio, handler, logger):
            super().__init__(bearer)
            self.socketio = socketio
            self.model_handler = handler
            self.logger = logger

        def on_tweet(self, tweet):
            try:
                text = tweet.text
                fake = self.model_handler.predict_fake_news(text)
                ai = self.model_handler.predict_ai_generated(text)
                payload = {
                    "source": "Twitter",
                    "headline": text,
                    "url": f"https://twitter.com/i/web/status/{tweet.id}",
                    "timestamp": str(datetime.utcnow()),
                    "fakeNews": {"prediction": fake["prediction"], "confidence": fake["confidence"]},
                    "aiGenerated": {"prediction": ai["prediction"], "confidence": ai["confidence"]}
                }
                self.socketio.emit("news_update", payload)
            except Exception as e:
                self.logger.error(f"Tweet processing failed: {e}")

    def start_stream(self, keywords):
        if not self.bearer_token:
            self.logger.warning("⚠️ Missing X_BEARER_TOKEN")
            return

        def run_stream():
            self.logger.info(f"Starting Twitter stream for: {keywords}")
            streamer = self.TweetStreamer(self.bearer_token, self.socketio, self.model_handler, self.logger)
            try:
                for rule in streamer.get_rules().data or []:
                    streamer.delete_rules(rule.id)
                streamer.add_rules(tweepy.StreamRule(" OR ".join(keywords)))
                streamer.filter(expansions=[], tweet_fields=["created_at", "lang"])
            except Exception as e:
                self.logger.error(f"❌ Error in stream: {e}")

        threading.Thread(target=run_stream, daemon=True).start()
