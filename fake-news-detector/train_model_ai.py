# train_model_ai.py - Train the AI-enhanced model
import sys
import os

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from model_ai import AIFakeNewsDetector

def main():
    print("=" * 60)
    print("🤖 AI-POWERED FAKE NEWS DETECTOR - TRAINING")
    print("=" * 60)
    print()
    
    print("Initializing AI detector...")
    detector = AIFakeNewsDetector()
    
    print("\nStarting training with AI enhancements...")
    print("This will use:")
    print("  ✓ TF-IDF vectorization (traditional ML)")
    print("  ✓ Sentiment analysis (emotional patterns)")
    print("  ✓ Linguistic features (clickbait, sensationalism)")
    print("  ✓ Semantic embeddings (meaning understanding)")
    print("  ✓ Ensemble learning (multiple models voting)")
    print()
    
    detector.train()
    
    print("\n" + "=" * 60)
    print("🎉 TRAINING COMPLETE!")
    print("=" * 60)
    print()
    
    # Test with sample articles
    print("Testing AI model with sample articles...\n")
    
    test_cases = [
        ("You won't BELIEVE what scientists discovered! Doctors HATE this one simple trick!", "Should be FAKE"),
        ("The Federal Reserve announced an interest rate increase of 0.25 percent today.", "Should be REAL"),
        ("BREAKING: URGENT ALERT! Government conspiracy EXPOSED in leaked documents!", "Should be FAKE"),
        ("Researchers at Stanford University published findings in the Journal of Medicine.", "Should be REAL"),
    ]
    
    for text, expected in test_cases:
        result = detector.analyze_text(text)
        print(f"Text: {text[:60]}...")
        print(f"Expected: {expected}")
        print(f"Prediction: {result['prediction']} (Confidence: {result['confidence']:.1%})")
        if 'warning_signs' in result and result['warning_signs']:
            print(f"Warning signs: {', '.join(result['warning_signs'])}")
        print()
    
    print("✅ AI model is ready to detect fake news beyond training data!")

if __name__ == "__main__":
    main()
