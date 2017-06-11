import os
import sys
import json
import random
import string
import requests
from flask import Flask, request



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
                    if "text" in messaging_event["message"]:
                    	message_text = messaging_event["message"]["text"]  # the message's text
                    	response = chooseMessage(message_text)
                    	send_message(sender_id, response)
                    if "sticker_id" in messaging_event["message"]:
                    	send_message(sender_id, "Thanks for the like!")


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
	if message.lower() == "who are you?" or message.lower() == "who are you":
		return "I am HAFS Newsbot, coded by Shawn Lee. I am designed to provide you with news, but I can't do that as of now."
	for word in message.lower().split():
		if word in ["fuck", "shit", "fucking"]:
			return random.choice(["Hey! Don't swear!", "You know, it isn't okay to swear..."])
	
	return random.choice(["I don't understand what you're saying.","Huh?","What do you mean?", "I can't understand much as of now. Try saying hi!"])

def chooseGreeting(message):
	GREETINGS_KEYWORDS = ["hello","hi","hey","sup","whats up","good morning","yo", "hi!","hai"]
	GREETINGS_RESPONSES = ["Hello!","Hi!","What's up?","How's it going?","Hey!"]

	for word in message.lower().split():
		if word in GREETINGS_KEYWORDS:
			return random.choice(GREETINGS_RESPONSES)

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
