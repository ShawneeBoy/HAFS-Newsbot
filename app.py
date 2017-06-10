#-*- coding: utf-8 -*-
import os
import sys
import json
import random
import string
import requests
from flask import Flask, request

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    response = chooseMessage(message_text)
                    send_message(sender_id, response)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200

def chooseMessage(message):
	if chooseGreeting(message):
		return chooseGreeting(message)
	if message.lower().translate(string.maketrans('','',string.punctuation)) == "who are you" or message.lower().translate(string.maketrans('','',string.punctuation)) == "what are you":
		return "I am HAFS Newsbot, coded by Shawn Lee. I am designed to provide you with news, but I can't do that as of now."
	if message.lower().translate(string.maketrans('','',string.punctuation)) in ["fuck", "shit", "fucking"]:
		return random.choice(["Hey! Don't swear!", "You know, it isn't okay to swear..."])

	
	return random.choice(["I don't understand what you're saying.","Huh?","What do you mean?"])

def chooseGreeting(message):
	GREETINGS_KEYWORDS = ["hello","hi","hey","sup","whats up","good morning","yo"]
	GREETINGS_RESPONSES = ["Hello!","Hi!","What's up?","How's it going?","Hey!"]
	GREETINGS_KEYWORDS_K = ["안녕", "안녕하세요", "하이", "ㅎㅇ"]
	GREETINGS_RESPONSES_K = ["안녕하세요!"]
	for word in message.split():
		if message.lower() in GREETINGS_KEYWORDS:
			return random.choice(GREETINGS_RESPONSES)
	if message.translate(string.maketrans('','',string.punctuation)) in GREETINGS_KEYWORDS_K:
		return random.choice(GREETINGS_RESPONSES_K)
	return False



def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
