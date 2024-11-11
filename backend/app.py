from flask import Flask, jsonify, redirect
from flask_cors import CORS
from main import GmailSummarizer
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)

summarizer = GmailSummarizer()

@app.route('/auth', methods=['GET'])
def auth():
    try:
        # This will trigger the Google OAuth flow and create token.pickle
        service = summarizer.authenticate()
        return jsonify({'status': 'authenticated'})
    except Exception as e:
        return jsonify({
            'error': 'auth_error',
            'message': str(e)
        }), 500

@app.route('/get-summary', methods=['GET'])
def get_summary():
    try:
        if not os.path.exists('token.pickle'):
            return jsonify({
                'error': 'not_authenticated',
                'message': 'Please authenticate with Google first'
            }), 401
            
        service = summarizer.authenticate()
        emails = summarizer.get_emails(service)
        summary = summarizer.summarize_emails(emails)
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({
            'error': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 