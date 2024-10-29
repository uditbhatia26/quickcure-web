from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # Allow CORS for cross-origin requests

# Retrieve environment variables
API_KEY = os.getenv("API_KEY", "rJkTxP36ksBIeAzvfIw9nYpTcXXxjBOp")  # Replace with default or ensure this is set
EXTERNAL_USER_ID = os.getenv("EXTERNAL_USER_ID")

# Check if critical environment variables are set
if API_KEY == "default_api_key_here" or not EXTERNAL_USER_ID:
    print("Warning: Critical environment variables (API_KEY or EXTERNAL_USER_ID) are missing.")

@app.route('/')
def index():
    return render_template('index.html')  # Existing index page

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')  # New chatbot page

@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.json.get('query')

    try:
        # Step 1: Create Chat Session
        create_session_url = 'https://api.on-demand.io/chat/v1/sessions'
        create_session_headers = {'apikey': API_KEY}
        create_session_body = {
            "pluginIds": [],
            "externalUserId": EXTERNAL_USER_ID
        }

        session_response = requests.post(create_session_url, headers=create_session_headers, json=create_session_body, timeout=10)
        session_response.raise_for_status()
        session_id = session_response.json()['data']['id']

        # Step 2: Submit User Query to the Bot
        submit_query_url = f'https://api.on-demand.io/chat/v1/sessions/{session_id}/query'
        submit_query_headers = {'apikey': API_KEY}
        submit_query_body = {
            "endpointId": "predefined-openai-gpt4o",
            "query": user_query,
            "pluginIds": ["plugin-1717464304"],
            "responseMode": "sync"
        }

        query_response = requests.post(submit_query_url, headers=submit_query_headers, json=submit_query_body, timeout=10)
        query_response.raise_for_status()
        answer = query_response.json()['data']['answer']

        return jsonify({"answer": answer})

    except requests.exceptions.Timeout:
        print("Request timed out.")
        return jsonify({"answer": "Sorry, the request timed out. Please try again later."}), 504

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return jsonify({"answer": "Sorry, I couldn't process your request."}), 500


if __name__ == "__main__":
    # Set port using an environment variable, with a default to 4000
    port = int(os.getenv("PORT", 4000))
    app.run(host="0.0.0.0", port=port)
