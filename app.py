import os
import logging
from flask import Flask, render_template, request, jsonify
from googletrans import Translator, LANGUAGES
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Initialize Google Translator
translator = Translator()

# Language codes and names mapping
LANGUAGE_MAPPING = {
    'auto': 'Auto Detect',
    'af': 'Afrikaans',
    'sq': 'Albanian',
    'ar': 'Arabic',
    'hy': 'Armenian',
    'az': 'Azerbaijani',
    'eu': 'Basque',
    'be': 'Belarusian',
    'bn': 'Bengali',
    'bs': 'Bosnian',
    'bg': 'Bulgarian',
    'ca': 'Catalan',
    'ceb': 'Cebuano',
    'ny': 'Chichewa',
    'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)',
    'co': 'Corsican',
    'hr': 'Croatian',
    'cs': 'Czech',
    'da': 'Danish',
    'nl': 'Dutch',
    'en': 'English',
    'eo': 'Esperanto',
    'et': 'Estonian',
    'tl': 'Filipino',
    'fi': 'Finnish',
    'fr': 'French',
    'fy': 'Frisian',
    'gl': 'Galician',
    'ka': 'Georgian',
    'de': 'German',
    'el': 'Greek',
    'gu': 'Gujarati',
    'ht': 'Haitian Creole',
    'ha': 'Hausa',
    'haw': 'Hawaiian',
    'iw': 'Hebrew',
    'hi': 'Hindi',
    'hmn': 'Hmong',
    'hu': 'Hungarian',
    'is': 'Icelandic',
    'ig': 'Igbo',
    'id': 'Indonesian',
    'ga': 'Irish',
    'it': 'Italian',
    'ja': 'Japanese',
    'jw': 'Javanese',
    'kn': 'Kannada',
    'kk': 'Kazakh',
    'km': 'Khmer',
    'ko': 'Korean',
    'ku': 'Kurdish (Kurmanji)',
    'ky': 'Kyrgyz',
    'lo': 'Lao',
    'la': 'Latin',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'lb': 'Luxembourgish',
    'mk': 'Macedonian',
    'mg': 'Malagasy',
    'ms': 'Malay',
    'ml': 'Malayalam',
    'mt': 'Maltese',
    'mi': 'Maori',
    'mr': 'Marathi',
    'mn': 'Mongolian',
    'my': 'Myanmar (Burmese)',
    'ne': 'Nepali',
    'no': 'Norwegian',
    'ps': 'Pashto',
    'fa': 'Persian',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'pa': 'Punjabi',
    'ro': 'Romanian',
    'ru': 'Russian',
    'sm': 'Samoan',
    'gd': 'Scots Gaelic',
    'sr': 'Serbian',
    'st': 'Sesotho',
    'sn': 'Shona',
    'sd': 'Sindhi',
    'si': 'Sinhala',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'so': 'Somali',
    'es': 'Spanish',
    'su': 'Sundanese',
    'sw': 'Swahili',
    'sv': 'Swedish',
    'tg': 'Tajik',
    'ta': 'Tamil',
    'te': 'Telugu',
    'th': 'Thai',
    'tr': 'Turkish',
    'uk': 'Ukrainian',
    'ur': 'Urdu',
    'uz': 'Uzbek',
    'vi': 'Vietnamese',
    'cy': 'Welsh',
    'xh': 'Xhosa',
    'yi': 'Yiddish',
    'yo': 'Yoruba',
    'zu': 'Zulu'
}

@app.route('/')
def index():
    """Render the main translation page"""
    return render_template('index.html', languages=LANGUAGE_MAPPING)

@app.route('/translate', methods=['POST'])
def translate_text():
    """Handle translation requests"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        source_lang = data.get('source', 'auto')
        target_lang = data.get('target', 'en')
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Please enter some text to translate'
            })
        
        if len(text) > 5000:
            return jsonify({
                'success': False,
                'error': 'Text is too long. Please limit to 5000 characters.'
            })
        
        # Perform translation
        result = translator.translate(text, src=source_lang, dest=target_lang)
        
        return jsonify({
            'success': True,
            'translated_text': result.text,
            'detected_language': result.src,
            'confidence': getattr(result.extra_data, 'confidence', None)
        })
        
    except Exception as e:
        app.logger.error(f"Translation error: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Translation service is currently unavailable. Please try again later.'
        })

@app.route('/detect', methods=['POST'])
def detect_language():
    """Detect the language of input text"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text or len(text) < 3:
            return jsonify({
                'success': False,
                'error': 'Please enter at least 3 characters for language detection'
            })
        
        detection = translator.detect(text)
        
        return jsonify({
            'success': True,
            'language': detection.lang,
            'confidence': detection.confidence
        })
        
    except Exception as e:
        app.logger.error(f"Language detection error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Language detection is currently unavailable'
        })

@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html', languages=LANGUAGE_MAPPING), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal server error: {str(error)}")
    return render_template('index.html', languages=LANGUAGE_MAPPING), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
