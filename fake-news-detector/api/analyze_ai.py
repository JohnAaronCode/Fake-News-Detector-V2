# analyze_ai.py - AI-powered analysis endpoint (lightweight for Vercel)
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import re

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from model import FakeNewsDetector

detector = FakeNewsDetector()

def extract_urls(text):
    """Extract all URLs from the text"""
    # URL regex pattern
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    
    # Also find www. links
    www_pattern = r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    www_urls = re.findall(www_pattern, text)
    
    # Add http:// to www links
    www_urls = ['http://' + url for url in www_urls]
    
    all_urls = list(set(urls + www_urls))  # Remove duplicates
    return all_urls

def analyze_url_credibility(url):
    """Analyze URL for credibility indicators"""
    url_lower = url.lower()
    
    # Trusted news sources
    trusted_domains = [
        'bbc.com', 'nytimes.com', 'wsj.com', 'reuters.com', 'apnews.com',
        'npr.org', 'cnn.com', 'abcnews.go.com', 'cbsnews.com', 'nbcnews.com',
        'theguardian.com', 'washingtonpost.com', 'bloomberg.com', 'forbes.com',
        'time.com', 'newsweek.com', 'politico.com', 'theatlantic.com',
        'economist.com', 'usatoday.com', 'latimes.com', 'chicagotribune.com',
        'gov', 'edu', 'mil'  # Government, education, military domains
    ]
    
    # Suspicious patterns
    suspicious_patterns = [
        'fake', 'hoax', 'conspiracy', 'truth', 'exposed', 'leaked',
        'secret', 'hidden', 'shocking', 'unbelievable', 'click', 'viral'
    ]
    
    credibility = 'unknown'
    
    # Check for trusted domains
    for domain in trusted_domains:
        if domain in url_lower:
            credibility = 'trusted'
            break
    
    # Check for suspicious patterns
    if credibility == 'unknown':
        for pattern in suspicious_patterns:
            if pattern in url_lower:
                credibility = 'suspicious'
                break
    
    # Extract domain name
    domain_match = re.search(r'://(?:www\.)?([^/]+)', url)
    domain = domain_match.group(1) if domain_match else url
    
    return {
        'url': url,
        'domain': domain,
        'credibility': credibility
    }

def extract_ai_features(text):
    """Extract AI features without heavy dependencies"""
    features = {}
    
    # Text statistics
    features['text_length'] = len(text)
    features['word_count'] = len(text.split())
    features['avg_word_length'] = sum(len(word) for word in text.split()) / (len(text.split()) or 1)
    
    # Punctuation and capitalization patterns (fake news often has excessive punctuation/caps)
    features['exclamation_count'] = text.count('!')
    features['question_count'] = text.count('?')
    features['caps_ratio'] = sum(1 for c in text if c.isupper()) / (len(text) or 1)
    features['digit_ratio'] = sum(1 for c in text if c.isdigit()) / (len(text) or 1)
    
    # Clickbait indicators
    clickbait_words = ['shocking', 'unbelievable', 'you wont believe', 'you won\'t believe', 
                      'this one trick', 'doctors hate', 'secret', 'revealed', 'exposed']
    features['clickbait_score'] = sum(1 for word in clickbait_words if word in text.lower())
    
    # Sensationalism indicators
    sensational_words = ['breaking', 'urgent', 'alert', 'warning', 'exclusive', 'leaked', 
                        'bombshell', 'scandal']
    features['sensational_score'] = sum(1 for word in sensational_words if word in text.lower())
    
    return features

def analyze_with_ai(text):
    """Analyze text with AI enhancements and link extraction"""
    # Get base prediction
    prediction, confidence = detector.predict(text)
    
    if prediction is None:
        return {
            'prediction': 'ERROR',
            'confidence': 0.0,
            'ai_powered': False,
            'error': 'Model not available'
        }
    
    label = "REAL" if prediction == 1 else "FAKE"
    
    # Extract URLs from text
    urls = extract_urls(text)
    analyzed_links = [analyze_url_credibility(url) for url in urls]
    
    # Count credibility types
    trusted_count = sum(1 for link in analyzed_links if link['credibility'] == 'trusted')
    suspicious_count = sum(1 for link in analyzed_links if link['credibility'] == 'suspicious')
    
    # Extract AI features
    features = extract_ai_features(text)
    
    # Adjust confidence based on AI features
    warning_signs = []
    confidence_adjustment = 0
    
    if features['clickbait_score'] > 2:
        warning_signs.append("High clickbait language detected")
        if label == "FAKE":
            confidence_adjustment += 0.05
    
    if features['sensational_score'] > 2:
        warning_signs.append("Sensationalist language present")
        if label == "FAKE":
            confidence_adjustment += 0.05
    
    if features['caps_ratio'] > 0.15:
        warning_signs.append("Excessive capitalization")
        if label == "FAKE":
            confidence_adjustment += 0.03
    
    if features['exclamation_count'] > 3:
        warning_signs.append("Excessive exclamation marks")
        if label == "FAKE":
            confidence_adjustment += 0.03
    
    # Link credibility analysis
    if suspicious_count > 0:
        warning_signs.append(f"Contains {suspicious_count} suspicious link(s)")
        if label == "FAKE":
            confidence_adjustment += 0.05
    
    if len(urls) > 0 and trusted_count == 0:
        warning_signs.append("No trusted news sources linked")
    
    # Adjust confidence (cap at 0.99)
    adjusted_confidence = min(0.99, confidence + confidence_adjustment)
    
    return {
        'prediction': label,
        'confidence': adjusted_confidence,
        'ai_powered': True,
        'warning_signs': warning_signs,
        'model_type': 'AI-Enhanced Ensemble (Logistic + Linguistic + Link Analysis)',
        'links': analyzed_links,
        'link_summary': {
            'total': len(urls),
            'trusted': trusted_count,
            'suspicious': suspicious_count,
            'unknown': len(urls) - trusted_count - suspicious_count
        }
    }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        try:
            # Get request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            text = data.get('text', '')
            
            if not text:
                response = {
                    'error': 'No text provided'
                }
            else:
                response = analyze_with_ai(text)
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            error_response = {
                'error': str(e),
                'prediction': 'ERROR',
                'confidence': 0.0
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
