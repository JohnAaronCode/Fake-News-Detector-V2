# model_ai.py - Lightweight AI-powered fake news detector (Vercel compatible)
import pandas as pd
import numpy as np
import joblib
import os
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score

# Lightweight AI imports (no torch/transformers for Vercel)
try:
    import nltk
    from textblob import TextBlob
    ADVANCED_FEATURES = True
    
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
        except:
            pass
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        try:
            nltk.download('stopwords', quiet=True)
        except:
            pass
        
except ImportError:
    ADVANCED_FEATURES = False


class AIFakeNewsDetector:
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        self.model_path = os.path.join(base_dir, "fake_news_model_ai.pkl")
        self.vectorizer_path = os.path.join(base_dir, "tfidf_vectorizer_ai.pkl")
        
        self.model = None
        self.vectorizer = None
        
        self.load_model()

    def extract_linguistic_features(self, text):
        """Extract advanced linguistic features for better generalization"""
        features = {}
        
        if not ADVANCED_FEATURES:
            # Basic features without external libraries
            features['text_length'] = len(text)
            features['word_count'] = len(text.split())
            features['avg_word_length'] = np.mean([len(word) for word in text.split()] or [0])
            features['exclamation_count'] = text.count('!')
            features['question_count'] = text.count('?')
            features['caps_ratio'] = sum(1 for c in text if c.isupper()) / (len(text) or 1)
            features['digit_ratio'] = sum(1 for c in text if c.isdigit()) / (len(text) or 1)
            
            clickbait_words = ['shocking', 'unbelievable', 'you wont believe', 'this one trick', 
                             'doctors hate', 'secret', 'revealed', 'exposed']
            features['clickbait_score'] = sum(1 for word in clickbait_words if word in text.lower())
            
            sensational_words = ['breaking', 'urgent', 'alert', 'warning', 'exclusive', 'leaked']
            features['sensational_score'] = sum(1 for word in sensational_words if word in text.lower())
            
            return features
        
        try:
            # Sentiment analysis
            blob = TextBlob(text)
            features['sentiment_polarity'] = blob.sentiment.polarity
            features['sentiment_subjectivity'] = blob.sentiment.subjectivity
            
            # Text statistics
            features['text_length'] = len(text)
            features['word_count'] = len(text.split())
            features['avg_word_length'] = np.mean([len(word) for word in text.split()] or [0])
            
            # Punctuation and capitalization patterns (fake news often has excessive punctuation/caps)
            features['exclamation_count'] = text.count('!')
            features['question_count'] = text.count('?')
            features['caps_ratio'] = sum(1 for c in text if c.isupper()) / (len(text) or 1)
            features['digit_ratio'] = sum(1 for c in text if c.isdigit()) / (len(text) or 1)
            
            # Clickbait indicators
            clickbait_words = ['shocking', 'unbelievable', 'you wont believe', 'this one trick', 
                             'doctors hate', 'secret', 'revealed', 'exposed']
            features['clickbait_score'] = sum(1 for word in clickbait_words if word in text.lower())
            
            # Sensationalism indicators
            sensational_words = ['breaking', 'urgent', 'alert', 'warning', 'exclusive', 'leaked']
            features['sensational_score'] = sum(1 for word in sensational_words if word in text.lower())
            
        except Exception as e:
            print(f"Error extracting linguistic features: {e}")
        
        return features

    def combine_features(self, text):
        """Combine TF-IDF and linguistic features"""
        features_list = []
        
        # 1. TF-IDF features (traditional)
        tfidf_features = self.vectorizer.transform([text]).toarray()[0]
        features_list.append(tfidf_features)
        
        # 2. Linguistic features (pattern detection)
        ling_features = self.extract_linguistic_features(text)
        ling_array = np.array(list(ling_features.values()))
        features_list.append(ling_array)
        
        # Combine all features
        combined = np.concatenate(features_list)
        return combined.reshape(1, -1)

    def train(self):
        """Train the AI model with enhanced features"""
        try:
            base_dir = os.path.dirname(__file__)
            
            # Try multiple paths to find the data files
            possible_paths = [
                (os.path.join(base_dir, 'data', 'fake.csv'), os.path.join(base_dir, 'data', 'true.csv')),
                (os.path.join(base_dir, '..', 'backend', 'data', 'fake.csv'), os.path.join(base_dir, '..', 'backend', 'data', 'true.csv')),
            ]
            
            fake_path = None
            true_path = None
            
            for fp, tp in possible_paths:
                if os.path.exists(fp) and os.path.exists(tp):
                    fake_path = fp
                    true_path = tp
                    break
            
            # Load datasets
            if not fake_path or not true_path:
                print("⚠️ CSV files not found, using sample data")
                fake_df = pd.DataFrame({
                    'text': [
                        "Aliens have landed on Earth according to secret NASA documents!",
                        "You won't believe this one weird trick that doctors hate!",
                        "The government is hiding a cure for cancer!",
                        "Celebrities are secretly lizard people!",
                        "5G towers are spreading the virus!",
                        "BREAKING: Shocking revelation will change everything!",
                        "This LEAKED document exposes the truth they don't want you to know!"
                    ]
                })
                true_df = pd.DataFrame({
                    'text': [
                        "The government announced a new policy to support farmers.",
                        "Scientists published research findings on climate change.",
                        "The president met with world leaders to discuss the economy.",
                        "Stock markets showed mixed results today.",
                        "Congress passed a new infrastructure bill.",
                        "Researchers at the university completed a five-year study.",
                        "The company reported quarterly earnings that met expectations."
                    ]
                })
            else:
                print("📚 Loading real datasets from CSV files...")
                fake_df = pd.read_csv(fake_path)
                true_df = pd.read_csv(true_path)
                
                # Sample data for performance
                fake_df = fake_df[['text']].sample(n=min(500, len(fake_df)), random_state=42)
                true_df = true_df[['text']].sample(n=min(500, len(true_df)), random_state=42)
                
                print(f"✅ Loaded {len(fake_df)} fake news articles")
                print(f"✅ Loaded {len(true_df)} true news articles")
            
            # Add labels
            fake_df['label'] = 0  # Fake
            true_df['label'] = 1  # Real
            
            # Combine and shuffle
            df = pd.concat([fake_df, true_df], ignore_index=True)
            df = df.sample(frac=1, random_state=42).reset_index(drop=True)
            
            print(f"📊 Total training samples: {len(df)}")
            
        except Exception as e:
            print(f"❌ Error loading CSV files: {e}")
            print("Using minimal fallback data")
            df = pd.DataFrame({
                'text': [
                    "The government announced a new policy to support farmers.",
                    "Aliens have landed on Earth according to secret NASA documents!",
                    "Scientists discovered a cure for cancer after decades of research.",
                    "You won't believe this shocking secret the government is hiding!",
                ],
                'label': [1, 0, 1, 0]
            })

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            df['text'], df['label'], test_size=0.2, random_state=42
        )

        # Train TF-IDF vectorizer
        print("🔧 Training TF-IDF vectorizer...")
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.vectorizer.fit(X_train)

        # Extract combined features for all samples
        print("🧠 Extracting AI features...")
        X_train_combined = []
        for text in X_train:
            combined = self.combine_features(text)
            X_train_combined.append(combined[0])
        
        X_train_combined = np.array(X_train_combined)
        
        print(f"📐 Feature dimension: {X_train_combined.shape[1]}")

        # Train ensemble model for better generalization
        print("🎯 Training AI ensemble model...")
        
        # Create ensemble of models
        lr_model = LogisticRegression(max_iter=2000, random_state=42)
        rf_model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=10)
        
        self.model = VotingClassifier(
            estimators=[('lr', lr_model), ('rf', rf_model)],
            voting='soft'
        )
        
        self.model.fit(X_train_combined, y_train)

        # Test accuracy
        X_test_combined = []
        for text in X_test:
            combined = self.combine_features(text)
            X_test_combined.append(combined[0])
        
        X_test_combined = np.array(X_test_combined)
        predictions = self.model.predict(X_test_combined)
        accuracy = accuracy_score(y_test, predictions)
        
        print(f"✅ Model accuracy: {accuracy:.2%}")

        # Save model and vectorizer
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.vectorizer, self.vectorizer_path)
        print("💾 AI model trained and saved successfully!")

    def load_model(self):
        """Load the trained AI model"""
        try:
            self.model = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vectorizer_path)
        except:
            pass

    def predict(self, text):
        """Predict with AI-enhanced features"""
        if not self.model or not self.vectorizer:
            return None, 0.0

        try:
            # Get combined features
            features = self.combine_features(text)
            
            # Make prediction
            prediction = self.model.predict(features)[0]
            confidence = max(self.model.predict_proba(features)[0])
            
            return prediction, confidence
        except Exception as e:
            print(f"Error during prediction: {e}")
            return None, 0.0

    def analyze_text(self, text):
        """Detailed analysis with explanations"""
        prediction, confidence = self.predict(text)
        
        if prediction is None:
            return {
                'prediction': 'Error',
                'confidence': 0.0,
                'analysis': 'Model not available'
            }
        
        result = {
            'prediction': 'REAL' if prediction == 1 else 'FAKE',
            'confidence': float(confidence),
        }
        
        # Add linguistic analysis
        features = self.extract_linguistic_features(text)
        result['linguistic_features'] = features
        
        # Provide reasoning
        reasons = []
        if features.get('clickbait_score', 0) > 2:
            reasons.append("High clickbait language detected")
        if features.get('sensational_score', 0) > 2:
            reasons.append("Sensationalist language present")
        if features.get('caps_ratio', 0) > 0.15:
            reasons.append("Excessive capitalization")
        if features.get('exclamation_count', 0) > 3:
            reasons.append("Excessive exclamation marks")
        if ADVANCED_FEATURES and abs(features.get('sentiment_polarity', 0)) > 0.5:
            reasons.append("Highly emotional tone")
        
        result['warning_signs'] = reasons
        
        return result
