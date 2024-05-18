from flask import Flask, request, jsonify, render_template
import requests
import logging
import os

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

EDEN_API_KEY = os.getenv('EDEN_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        if not user_message:
            app.logger.error('No message provided')
            return jsonify({'error': 'No message provided'}), 400

        # Call Eden AI API
        response = eden_ai_call(user_message)
        app.logger.debug(f'Eden AI response: {response}')

        return jsonify({'response': response})
    except Exception as e:
        app.logger.exception('Error processing the request')
        return jsonify({'error': 'Internal Server Error'}), 500

def eden_ai_call(message):
    url = "https://api.edenai.run/v2/text/generation"  # Correct API endpoint

    payload = {
        "text": message,
        "providers": ["openai"],
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {EDEN_API_KEY}"
    }

    response = requests.post(url, json=payload, headers=headers)
    
    try:
        response.raise_for_status()
        response_data = response.json()
    except requests.exceptions.HTTPError as http_err:
        app.logger.error(f'HTTP error occurred: {http_err} - {response.text}')
        return f"HTTP error: {http_err}"
    except requests.exceptions.RequestException as err:
        app.logger.error(f'Request exception occurred: {err}')
        return f"Request error: {err}"
    except ValueError as json_err:
        app.logger.error(f'JSON decode error: {json_err}')
        return "Error: Unable to decode the JSON response."

    if "openai" in response_data and response_data["openai"]["status"] == "success":
        return response_data["openai"]["generated_text"]
    else:
        app.logger.error(f'Error from Eden AI API: {response_data}')
        return "Error: Unable to process the request."

if __name__ == '__main__':
    app.run(debug=True)

