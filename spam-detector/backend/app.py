"""
Flask API Application - REST API for Spam & Malware Detection
A Simplified Heuristic-Based Implementation for College Presentations.
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import email
from email import policy

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'eml', 'txt', 'msg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------------------------------------------------
# Heuristic Engines (Simple Rules for Spam & Malware)
# -------------------------------------------------------------

def analyze_for_spam(text):
    """
    Simple keyword and pattern-based Spam detector.
    Instead of complex Machine Learning, this looks for common spam triggers.
    """
    # Use lowercase for easier matching
    text_lower = text.lower()
    spam_score = 0.0
    
    # Common Spam Keywords (Expanded for better detection)
    spam_keywords = [
        'free', 'money', 'winner', 'lottery', 'urgent', 'act now', 'click here', 
        'viagra', 'cash prize', 'exclusive deal', 'bank account', 'guaranteed',
        'wire transfer', 'nigerian prince', 'dear friend', 'buy now', 'offer',
        'discount', 'selected', 'claim', 'invest', 'crypto', 'bitcoin', '100%',
        'millions', 'pharmacy', 'weight loss', 'credit card', 'debt', 'loan'
    ]
    
    for kw in spam_keywords:
        if kw in text_lower:
            spam_score += 0.25  # Increased weight per keyword
            
    # Pattern: ALL CAPS (If more than 40% of the raw text is uppercase)
    caps_count = sum(1 for c in text if c.isupper())
    if len(text) > 20 and (caps_count / len(text)) > 0.40:
         spam_score += 0.30  # Heavy ALL CAPS usage is suspicious
         
    # Pattern: Too many exclamation marks
    if text.count('!') > 4:
         spam_score += 0.20
         
    # Pattern: Multiple Dollar Signs
    if text.count('$') > 3:
         spam_score += 0.20
         
    # Cap confidence at 99%
    confidence = min(0.99, spam_score)
    is_spam = confidence > 0.40  # Lowered threshold to ensure better detection of pasted spam text
    
    return is_spam, confidence

def analyze_for_malware(text, filename=None):
    """
    Simple heuristic Malware detector.
    Looks for dangerous file extensions and payload keywords like trojan.
    """
    text_lower = text.lower()
    malware_score = 0.0
    
    # 1. Check for malicious keywords in the email body
    malicious_keywords = [
        'payload', 'trojan', 'ransomware', 'virus', 'malware', 
        'bitcoin address', 'password reset link', 'download this .exe',
        'turn off your antivirus', 'install this file'
    ]
    
    for kw in malicious_keywords:
        if kw in text_lower:
            malware_score += 0.45  # Massive jump per keyword
            
    # 2. Check for suspicious phishing/malware patterns
    if "http" in text_lower and ("login" in text_lower or "bank" in text_lower or "verify" in text_lower):
        malware_score += 0.25
        
    # 3. If an uploaded file itself has a dangerous embedded extension in its body
    if ".exe" in text_lower or ".bat" in text_lower or ".vbs" in text_lower:
        malware_score += 0.35

    # Cap confidence
    confidence = min(0.99, malware_score)
    is_malware = confidence > 0.50
    
    return is_malware, confidence
    
# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------

@app.route('/api/analyze-text', methods=['POST'])
def analyze_text():
    try:
        data = request.get_json()
        if not data or 'email_text' not in data:
            return jsonify({'error': 'No email text provided'}), 400
            
        email_text = data['email_text']
        
        # Run both simple heuristic engines
        is_spam, spam_confidence = analyze_for_spam(email_text)
        is_malware, malware_confidence = analyze_for_malware(email_text)
        
        return jsonify({
            'is_spam': is_spam,
            'spam_confidence': spam_confidence,
            'is_malware': is_malware,
            'malware_confidence': malware_confidence,
            'label': 'Spam' if is_spam else 'Ham',
            'analysis_type': 'text'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-file', methods=['POST'])
def analyze_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Allowed: .eml, .txt, .msg'}), 400
            
        # Parse text from file properly using Python's built-in email parser
        raw_bytes = file.read()
        
        # Default to raw string
        content = raw_bytes.decode('utf-8', errors='ignore')
        
        # If it's an .eml file, properly decode the MIME body instead of reading raw headers
        if file.filename.lower().endswith('.eml'):
            try:
                msg = email.message_from_bytes(raw_bytes, policy=policy.default)
                body_parts = []
                for part in msg.walk():
                    # Only grab text/plain or text/html bodies, avoiding raw encoded attachments
                    if part.get_content_type() in ["text/plain", "text/html"]:
                        try:
                            body_parts.append(part.get_content())
                        except:
                            pass
                if body_parts:
                    content = "\n".join(body_parts) # Replace raw string with properly decoded text
            except Exception as e:
                print("Could not parse EML properly, falling back to raw text:", e)
        
        # Run heuristic engines
        is_spam, spam_confidence = analyze_for_spam(content)
        is_malware, malware_confidence = analyze_for_malware(content, filename=file.filename)
        
        return jsonify({
            'is_spam': is_spam,
            'spam_confidence': spam_confidence,
            'is_malware': is_malware,
            'malware_confidence': malware_confidence,
            'label': 'Spam' if is_spam else 'Ham',
            'analysis_type': 'file'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------------------------------------------
# Static File Routes (HTML/JS/CSS)
# -------------------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    return send_from_directory(frontend_path, 'index.html')

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    if path.startswith('api/'):
        return jsonify({'error': 'Use /api/ prefix for API requests'}), 404
        
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    try:
        return send_from_directory(frontend_path, path)
    except:
        return send_from_directory(frontend_path, 'index.html')

if __name__ == '__main__':
    print("\n=============================================")
    print("Simple Heuristic Spam & Malware Detector Started!")
    print("Serving Web UI at: http://127.0.0.1:5000/")
    print("=============================================\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
