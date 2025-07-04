from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.github_webhook
collection = db.events

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.headers.get('X-GitHub-Event')
    payload = request.json
    message = ""

    if event == 'push':
        author = payload['pusher']['name']
        branch = payload['ref'].split('/')[-1]
        message = f'{author} pushed to {branch} on {datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")}'

    elif event == 'pull_request':
        action = payload['action']
        is_merged = payload['pull_request'].get('merged', False)

        if action == 'opened':
            author = payload['sender']['login']
            from_branch = payload['pull_request']['head']['ref']
            to_branch = payload['pull_request']['base']['ref']
            message = f'{author} submitted a pull request from {from_branch} to {to_branch} on {datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")}'

        elif action == 'closed' and is_merged:
            author = payload['sender']['login']
            from_branch = payload['pull_request']['head']['ref']
            to_branch = payload['pull_request']['base']['ref']
            message = f'{author} merged branch {from_branch} to {to_branch} on {datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")}'

    else:
        return jsonify({"msg": "Event not handled"}), 200

    collection.insert_one({"message": message, "timestamp": datetime.utcnow()})
    return jsonify({"msg": "Data saved"}), 200


@app.route('/events')
def events():
    data = list(collection.find({}, {'_id': 0}))
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=5000)
