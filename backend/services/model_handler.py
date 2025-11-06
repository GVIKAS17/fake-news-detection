import joblib
import numpy as np
import time
import re
from pathlib import Path
import logging

try:
    import requests
    from bs4 import BeautifulSoup
    URL_EXTRACTION_AVAILABLE = True
except ImportError:
    URL_EXTRACTION_AVAILABLE = False

logger = logging.getLogger(__name__)

class ModelHandler:
    def __init__(self, model_dir=None):
        self.models_loaded = False
        self.fake_news_model = None
        self.ai_detector_model = None
        self.vectorizer = None
        self.models_dir = Path(r"C:\Users\vikas\OneDrive\Pictures\fiii\backend\models").resolve()
        logger.info(f"🧠 Loading models from {self.models_dir}")
        self.load_models()

    def load_models(self):
        try:
            fake_news_path = self.models_dir / "fake_news_model.joblib"
            ai_detector_path = self.models_dir / "ai_detector_model.joblib"
            vectorizer_path = self.models_dir / "vectorizer.joblib"
            if fake_news_path.exists():
                self.fake_news_model = joblib.load(fake_news_path)
                logger.info(f"✅ Fake News model loaded: {fake_news_path.name}")
            else:
                logger.warning(f"⚠️ Missing Fake News model: {fake_news_path}")
            if ai_detector_path.exists():
                self.ai_detector_model = joblib.load(ai_detector_path)
                logger.info(f"✅ AI Detector model loaded: {ai_detector_path.name}")
            else:
                logger.warning(f"⚠️ Missing AI Detector model: {ai_detector_path}")
            if vectorizer_path.exists():
                self.vectorizer = joblib.load(vectorizer_path)
                logger.info(f"✅ Vectorizer loaded: {vectorizer_path.name}")
            else:
                logger.warning(f"⚠️ Missing Vectorizer: {vectorizer_path}")
            self.models_loaded = all([self.fake_news_model, self.ai_detector_model, self.vectorizer])
            logger.info("🎯 All models loaded successfully." if self.models_loaded else "⚠️ Some models are missing. Using mock predictions.")
        except Exception as e:
            logger.error(f"❌ Model loading failed: {str(e)}")
            self.models_loaded = False

    def preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r"http\S+|www\S+|https\S+", "", text)
        text = re.sub(r"[^a-zA-Z\s]", "", text)
        return " ".join(text.split())

    def predict_fake_news(self, text):
        start = time.time()
        try:
            processed = self.preprocess_text(text)
            if not self.fake_news_model:
                return self._get_mock_fake_news_prediction()
            if hasattr(self.fake_news_model, "named_steps"):
                vec = [processed]
            elif self.vectorizer:
                vec = self.vectorizer.transform([processed])
            else:
                return self._get_mock_fake_news_prediction()
            pred = self.fake_news_model.predict(vec)[0]
            confidence = float(np.max(self.fake_news_model.predict_proba(vec)[0]) * 100) if hasattr(self.fake_news_model, "predict_proba") else 85.0
            label = "Real News" if pred == 1 else "Fake News"
            return {
                "prediction": label,
                "confidence": round(confidence, 2),
                "credibility_score": round(confidence if pred == 1 else (100 - confidence), 1),
                "bias_level": self._calculate_bias_level(confidence),
                "factual_accuracy": round(confidence, 1),
                "analysis_time": round(time.time() - start, 2)
            }
        except Exception as e:
            logger.error(f"❌ Fake news prediction error: {str(e)}")
            return self._get_mock_fake_news_prediction()

    def predict_ai_generated(self, text):
        start = time.time()
        try:
            processed = self.preprocess_text(text)
            if not self.ai_detector_model:
                return self._get_mock_ai_prediction()
            if hasattr(self.ai_detector_model, "named_steps"):
                vec = [processed]
            elif self.vectorizer:
                vec = self.vectorizer.transform([processed])
            else:
                return self._get_mock_ai_prediction()
            pred = self.ai_detector_model.predict(vec)[0]
            confidence = float(np.max(self.ai_detector_model.predict_proba(vec)[0]) * 100) if hasattr(self.ai_detector_model, "predict_proba") else 82.0
            label = "Human Written" if pred == 1 else "AI Generated"
            return {
                "prediction": label,
                "confidence": round(confidence, 2),
                "human_likelihood": round(confidence if pred == 1 else (100 - confidence), 1),
                "language_complexity": self._calculate_language_complexity(confidence),
                "pattern_score": round(confidence, 1),
                "analysis_time": round(time.time() - start, 2)
            }
        except Exception as e:
            logger.error(f"❌ AI detection error: {str(e)}")
            return self._get_mock_ai_prediction()

    def extract_text_from_url(self, url):
        if not URL_EXTRACTION_AVAILABLE:
            return None
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            for tag in soup(["script", "style"]):
                tag.decompose()
            return " ".join(line.strip() for line in soup.get_text().splitlines() if line.strip())
        except Exception as e:
            logger.error(f"❌ URL extraction error: {str(e)}")
            return None

    def _calculate_bias_level(self, confidence):
        return "Low" if confidence > 80 else "Medium" if confidence > 60 else "High"

    def _calculate_language_complexity(self, confidence):
        return "Natural" if confidence > 75 else "Somewhat Artificial" if confidence > 50 else "Highly Artificial"

    def _get_mock_fake_news_prediction(self):
        return {
            "prediction": "Real News",
            "confidence": 85.5,
            "credibility_score": 82.3,
            "bias_level": "Low",
            "factual_accuracy": 85.5,
            "analysis_time": 0.15
        }

    def _get_mock_ai_prediction(self):
        return {
            "prediction": "Human Written",
            "confidence": 78.2,
            "human_likelihood": 78.2,
            "language_complexity": "Natural",
            "pattern_score": 75.8,
            "analysis_time": 0.12
        }
