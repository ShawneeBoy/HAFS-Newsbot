
import os
import sys
import json
import random
import string
import requests
import urllib2
import urllib
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

                    if "text" in messaging_event["message"]:			# if the message contains text
                    	message_text = messaging_event["message"]["text"]  # the message's text
                    	if message_text.lower() == "news":
                    		send_quick_reply(sender_id)
                    	elif message_text.lower() == "help":
                    		send_message(sender_id, "Commands\n\n\tnews - Shows major news sites.\n\nMore commands to be added!")
                    	else:
                    		response = chooseMessage(message_text)
                    		send_message(sender_id, response)
                    		send_message(sender_id, "Type \"help\" for help on commands!")
                    	
                    if "sticker_id" in messaging_event["message"]:		#if the message contains a sticker
                    	stickerid = messaging_event["message"]["sticker_id"]
                    	replySticker(sender_id,stickerid)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200

def replySticker(sender_id,stickerid):
	if stickerid == 369239263222822 or stickerid == 369239383222810 or stickerid == 369239343222814:
		send_message(sender_id, random.choice(["Thanks for the like!","I like you too!","I like that like!"]))
	else:
		send_message(sender_id, random.choice(["You're a good sticker picker!","Nice sticker!","Stickers and stones may break my bones..."]))

def chooseMessage(message):

	if chooseGreeting(message):
		return chooseGreeting(message)
	if message.lower() == "who are you?" or message.lower() == "who are you":
		return "I am HAFS Newsbot, coded by Shawn Lee. I am designed to provide you with news."

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
	if message.lower() == "how are you?" or message.lower() == "how are you":
		return "I'm doing fine, thank you!"

	return False

def send_news_message(recipient_id):
	send_quick_reply(recipient_id)


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

def send_quick_reply(recipient_id):

    log("sending quick replies to {recipient}".format(recipient=recipient_id))

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
            "text": "What news provider do you want?",
      		"quick_replies" : [
        	{
          		"content_type":"text",
          		"title":"CNN",
          		"payload":"choice_cnn",
          		"image_url":"http://petersfantastichats.com/img/red.png"
        	},
        	{
          		"content_type":"text",
          		"title":"The New York Times",
          		"payload":"choice_nyt",
          		"image_url":"http://petersfantastichats.com/img/red.png"
        	},
        	{
          		"content_type":"text",
          		"title":"ESPN",
          		"payload":"choice_espn",
          		"image_url":"http://petersfantastichats.com/img/red.png"
        	}
      		]
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def send_newsblock_message(recipient_id, newsType):

    log("sending news message to {recipient}".format(recipient=recipient_id))
    response = urllib2.urlopen('https://newsapi.org/v1/articles?source=cnn&sortBy=top&apiKey=09fb3aeaa2a742fcb02dedb105bad7ae')
    
    data = json.load(response)
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
            "attachment": {
        "type": "template",
        "payload": {
          "template_type": "generic",
          "elements": [{
            "title": data["articles"][0]["title"],
            "subtitle": data["articles"][0]["description"],
            "item_url": data["articles"][0]["url"],     
            "image_url": data["articles"][0]["urlToImage"],
            "buttons": [{
              "type": "web_url",
              "url": data["articles"][0]["url"],
              "title": "Read more"
            }],
          },{
            "title": data["articles"][1]["title"],
            "subtitle": data["articles"][1]["description"],
            "item_url": data["articles"][1]["url"],     
            "image_url": data["articles"][1]["urlToImage"],
            "buttons": [{
              "type": "web_url",
              "url": data["articles"][1]["url"],
              "title": "Read more"
            }],
          },{
          	"title": data["articles"][2]["title"],
            "subtitle": data["articles"][2]["description"],
            "item_url": data["articles"][2]["url"],     
            "image_url": data["articles"][2]["urlToImage"],
            "buttons": [{
              "type": "web_url",
              "url": cnn_data["articles"][2]["url"],
              "title": "Read more"
            }],
       	  }]
          	
        }
      }
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
