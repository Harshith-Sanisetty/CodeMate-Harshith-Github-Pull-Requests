

from flask import Flask, request, jsonify
from harshith_pr_agent.services.review_service import run_graph_review, run_chatbot_response, BOT_SIGNATURE
import threading
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

BOT_TRIGGER_PHRASE = "Harshith PR Agent"

def run_review_in_background(pr_url):
    print(f"--- [Thread] Starting full analysis for {pr_url} ---")
    try:
        run_graph_review(pr_url, post_to_github=True)
        print(f"--- [Thread] Full analysis for {pr_url} completed. ---")
    except Exception as e:
        print(f"--- [Thread] Error during full analysis for {pr_url}: {e} ---")

def run_chatbot_in_background(pr_url, comment_body):
    print(f"--- [Thread] Starting chatbot response for {pr_url} ---")
    try:
        run_chatbot_response(pr_url, comment_body)
        print(f"--- [Thread] Chatbot response for {pr_url} completed. ---")
    except Exception as e:
        print(f"--- [Thread] Error during chatbot response for {pr_url}: {e} ---")

@app.route('/webhook', methods=['POST'])
def github_webhook():
    payload = request.get_json()
    if not payload:
        return jsonify({'status': 'Invalid payload'}), 400

    
    if payload.get('action') == 'opened' and 'pull_request' in payload:
        pr_url = payload.get('pull_request', {}).get('html_url')
        if pr_url:
            print(f"--- [Webhook] Received new PR: {pr_url} ---")
            thread = threading.Thread(target=run_review_in_background, args=(pr_url,))
            thread.start()
            return jsonify({'status': 'Initial review process started'}), 200

    
    if payload.get('action') == 'created' and 'comment' in payload and 'issue' in payload:
        if 'pull_request' in payload.get('issue', {}):
            comment_body = payload.get('comment', {}).get('body', '')

            
            if BOT_SIGNATURE in comment_body:
                return jsonify({'status': 'Comment from bot itself, ignoring'}), 200

            if BOT_TRIGGER_PHRASE.lower() in comment_body.lower():
                pr_url = payload.get('issue', {}).get('pull_request', {}).get('html_url')
                if pr_url:
                    print(f"--- [Webhook] Chatbot query received on PR: {pr_url} ---")
                    thread = threading.Thread(target=run_chatbot_in_background, args=(pr_url, comment_body))
                    thread.start()
                    return jsonify({'status': 'Chatbot response process started'}), 200

    return jsonify({'status': 'Event not processed'}), 202

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)