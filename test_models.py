import joblib
import os
from pathlib import Path

def test_models():
    print("🧪 Testing Model Loading...\n")
    
    models_dir = Path('models')
    
    if not models_dir.exists():
        print("❌ Error: 'models' directory not found!")
        print("   Create it with: mkdir models")
        return False
    
    print(" Files in models directory:")
    files = list(models_dir.glob('*'))
    if not files:
        print(" !!!!!!!!! No files found in models directory!")
        return False
    
    for file in files:
        print(f"OOOKK : {file.name}")
    print()

    success = True
    
    fake_news_path = models_dir / 'fake_news_model.joblib'
    if not fake_news_path.exists():
        fake_news_path = models_dir / 'fake_news_model.pkl'
    
    if fake_news_path.exists():
        try:
            model = joblib.load(fake_news_path)
            print(f"✅ Fake News Model loaded successfully from {fake_news_path.name}")
            print(f"   Type: {type(model).__name__}")
            print(f"   Has predict: {hasattr(model, 'predict')}")
            print(f"   Has predict_proba: {hasattr(model, 'predict_proba')}")
        except Exception as e:
            print(f"❌ Error loading Fake News Model: {str(e)}")
            success = False
    else:
        print("⚠️  Fake News Model not found")
        print("   Looking for: fake_news_model.joblib or fake_news_model.pkl")
        print("   Please add your trained model to the models/ directory")
    
    print()
    
    ai_detector_path = models_dir / 'ai_detector_model.joblib'
    if not ai_detector_path.exists():
        ai_detector_path = models_dir / 'ai_detector_model.pkl'
    
    if ai_detector_path.exists():
        try:
            model = joblib.load(ai_detector_path)
            print(f"✅ AI Detector Model loaded successfully from {ai_detector_path.name}")
            print(f"   Type: {type(model).__name__}")
            print(f"   Has predict: {hasattr(model, 'predict')}")
            print(f"   Has predict_proba: {hasattr(model, 'predict_proba')}")
        except Exception as e:
            print(f"❌ Error loading AI Detector Model: {str(e)}")
            success = False
    else:
        print("⚠️  AI Detector Model not found")
        print("   Looking for: ai_detector_model.joblib or ai_detector_model.pkl")
        print("   Please add your trained model to the models/ directory")
    
    print()
    
    vectorizer_path = models_dir / 'vectorizer.joblib'
    if not vectorizer_path.exists():
        vectorizer_path = models_dir / 'vectorizer.pkl'
    
    if vectorizer_path.exists():
        try:
            vectorizer = joblib.load(vectorizer_path)
            print(f"✅ Vectorizer loaded successfully from {vectorizer_path.name}")
            print(f"   Type: {type(vectorizer).__name__}")
            print(f"   Has transform: {hasattr(vectorizer, 'transform')}")
            if hasattr(vectorizer, 'vocabulary_'):
                print(f"   Vocabulary size: {len(vectorizer.vocabulary_)}")
        except Exception as e:
            print(f"❌ Error loading Vectorizer: {str(e)}")
            success = False
    else:
        print("⚠️  Vectorizer not found")
        print("   Looking for: vectorizer.joblib or vectorizer.pkl")
        print("   If your model uses a vectorizer, please add it to models/")
    
    print()
    
    if success and fake_news_path.exists() and vectorizer_path.exists():
        print("🧪 Testing prediction on sample text...")
        try:
            test_text = "This is a test news article about politics."
            
            fake_news_model = joblib.load(fake_news_path)
            vectorizer = joblib.load(vectorizer_path)
            
            text_vec = vectorizer.transform([test_text])
            
            prediction = fake_news_model.predict(text_vec)[0]
            print(f"✅ Prediction successful: {prediction}")
            
            if hasattr(fake_news_model, 'predict_proba'):
                proba = fake_news_model.predict_proba(text_vec)[0]
                print(f"   Probabilities: {proba}")
                print(f"   Confidence: {max(proba) * 100:.2f}%")
        
        except Exception as e:
            print(f"❌ Error during prediction test: {str(e)}")
            success = False
    
    print()
    print("="*50)
    if success:
        print("✅ All tests passed! Your models are ready to use.")
        print("   Run 'python app.py' to start the Flask server")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    print("="*50)
    
    return success

if __name__ == "__main__":
    test_models()