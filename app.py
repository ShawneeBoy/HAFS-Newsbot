#-*- coding: utf-8 -*-

import os
import sys
import json
import random
import string
import requests
import urllib2
import urllib
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

                    if "text" in messaging_event["message"]:			# if the message contains text
                    	message_text = messaging_event["message"]["text"]  # the message's text
                    	processMessage(message_text, sender_id)
                    	
                    if "sticker_id" in messaging_event["message"]:		#if the message contains a sticker
                    	stickerid = messaging_event["message"]["sticker_id"]
                    	replySticker(sender_id,stickerid)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                	message_payload = messaging_event["postback"]["payload"]
                	if message_payload == "GET_STARTED":
                		send_message(sender_id, "Hello! I am Newsbot, designed to provide you with the latest news from a variety of news sources.")
                		send_message(sender_id, "Type \"news\" to get a list of news sites you can choose from!")
                    

    return "ok", 200




def processMessage(message_text, sender_id):
    if message_text.lower() == "news":
	send_quick_reply(sender_id)
    elif message_text.lower() == "cnn":
    	send_message(sender_id, "Giving you the latest news from " + message_text + "!")
    	send_news_message(sender_id,"cnn")
    elif message_text.lower() == "the new york times":
    	send_message(sender_id, "Giving you the latest news from " + message_text + "!")
	send_news_message(sender_id,"nyt")
    elif message_text.lower() == "espn":
    	send_message(sender_id, "Giving you the latest news from " + message_text + "!")
	send_news_message(sender_id,"espn")
    elif message_text.lower() == "time":
    	send_message(sender_id, "Giving you the latest news from " + message_text + "!")
    	send_news_message(sender_id,"time")
    elif message_text.lower() == "national geographic":
    	send_message(sender_id, "Giving you the latest news from " + message_text + "!")
    	send_news_message(sender_id,"natgeo")
    elif message_text.lower() == "bbc":
    	send_message(sender_id, "Giving you the latest news from " + message_text + "!")
    	send_news_message(sender_id,"bbc")
    elif message_text.lower() == "reddit":
    	send_message(sender_id, "Giving you the latest news from " + message_text + "!")
    	send_news_message(sender_id,"reddit")
    elif message_text.lower() == "buzzfeed":
    	send_message(sender_id, "Giving you the latest news from " + message_text + "!")
    	send_news_message(sender_id,"buzzfeed")
    elif message_text.lower() == "ign":
    	send_message(sender_id, "Giving you the latest news from " + message_text + "!")
    	send_news_message(sender_id,"ign")
    elif message_text.lower() == "the economist":
    	send_message(sender_id, "Giving you the latest news from " + message_text + "!")
    	send_news_message(sender_id,"econ")
    elif message_text.lower() == "help":
    	send_message(sender_id, "Type \"news\" for major news sites! \nMore functionality is to be added, including support for Korean and Korean news.")
    else:
    	response = defaultMessage(message_text)
    	send_message(sender_id, response)
    	





def replySticker(sender_id,stickerid):
	if stickerid == 369239263222822 or stickerid == 369239383222810 or stickerid == 369239343222814:
	    send_message(sender_id, random.choice(["Thanks for the like!","I like you too!","I like that like!"]))
	else:
	    send_message(sender_id, random.choice(["You're a good sticker picker!","Nice sticker!","Stickers and stones may break my bones..."]))




def defaultMessage(message):

	if chooseGreeting(message):
	    return chooseGreeting(message)
	if message.lower() == "who are you?" or message.lower() == "who are you":
	    return "I am HAFS Newsbot, coded by Shawn Lee. I am designed to provide you with news."

	for word in message.lower().split():
		if word in ["fuck", "shit", "fucking"]:
			return random.choice(["Hey! Don't swear!", "You know, it isn't okay tho swear..."])
	
	return random.choice(["I don't understand what you're saying.","Huh?","What do you mean?", "I can't understand much as of now. Try saying hi!"]) + "\nType \"help\" for help on commands!"






def chooseGreeting(message):
	GREETINGS_KEYWORDS = ["hello","hi","hey","sup","whats up","good morning","yo", "hi!","hai"]
	GREETINGS_RESPONSES = ["Hello!","Hi!","What's up?","How's it going?","Hey!"]

	for word in message.lower().split():
		if word in GREETINGS_KEYWORDS:

			return random.choice(GREETINGS_RESPONSES)
	if message.lower() == "how are you?" or message.lower() == "how are you":
		return "I'm doing fine, thank you!"

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
          		"image_url":"http://i.cdn.cnn.com/cnn/.e/img/3.0/global/misc/apple-touch-icon.png"
        	},
        	{
          		"content_type":"text",
          		"title":"The New York Times",
          		"payload":"choice_nyt",
          		"image_url":"https://mobile.nytimes.com/vi-assets/apple-touch-icon-319373aaf4524d94d38aa599c56b8655.png"
        	},
        	{
          		"content_type":"text",
          		"title":"ESPN",
          		"payload":"choice_espn",
          		"image_url":"http://a.espncdn.com/wireless/mw5/r1/images/bookmark-icons/espn_icon-152x152.min.png"
        	},
        	{
          		"content_type":"text",
          		"title":"Time",
          		"payload":"choice_time",
          		"image_url":"http://s0.wp.com/wp-content/themes/vip/time2014/img/time-touch_icon_120.png"
        	},
        	{
          		"content_type":"text",
          		"title":"National Geographic",
          		"payload":"choice_natgeo",
          		"image_url":"http://images.nationalgeographic.com/wpf/sites/common/i/presentation/NGLogo560x430-cb1343821768.png"
        	},
        	{
          		"content_type":"text",
          		"title":"BBC",
          		"payload":"choice_bbc",
          		"image_url":"http://m.files.bbci.co.uk/modules/bbc-morph-news-waf-page-meta/1.2.0/apple-touch-icon.png"
        	},
        	{
          		"content_type":"text",
          		"title":"Reddit",
          		"payload":"choice_reddit",
          		"image_url":"https://www.redditstatic.com/mweb2x/favicon/120x120.png"
        	},
        	{
          		"content_type":"text",
          		"title":"Buzzfeed",
          		"payload":"choice_buzzfeed",
          		"image_url":"https://www.buzzfeed.com/static-assets/img/touch-icon-ios_120.208a0e329cd6e8d831b21ae17fb6aabb.png"
        	},
        	{
          		"content_type":"text",
          		"title":"IGN",
          		"payload":"choice_ign",
          		"image_url":"http://m.ign.com/apple-touch-icon-precomposed.png"
        	},
        	{
          		"content_type":"text",
          		"title":"The Economist",
          		"payload":"choice_econ",
          		"image_url":"https://lh3.googleusercontent.com/j0rfLNcDw7hmSdKKXH88JA6tG6WKANNPIg1_9prDyLL2nLEUESd47CfTmyH1JLpTxxoD=w300"
        	}
      		]
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)





def send_news_message(recipient_id, newsType):

    log("sending news message to {recipient}".format(recipient=recipient_id))

    if newsType == "cnn":
    	response = urllib2.urlopen('https://newsapi.org/v1/articles?source=cnn&sortBy=top&apiKey=09fb3aeaa2a742fcb02dedb105bad7ae')
    elif newsType == "nyt":
    	response = urllib2.urlopen('https://newsapi.org/v1/articles?source=the-new-york-times&sortBy=top&apiKey=09fb3aeaa2a742fcb02dedb105bad7ae')
    elif newsType == "espn":
    	response = urllib2.urlopen('https://newsapi.org/v1/articles?source=espn&sortBy=top&apiKey=09fb3aeaa2a742fcb02dedb105bad7ae')
    elif newsType == "time":
    	response = urllib2.urlopen('https://newsapi.org/v1/articles?source=time&sortBy=top&apiKey=09fb3aeaa2a742fcb02dedb105bad7ae')
    elif newsType == "natgeo":
    	response = urllib2.urlopen('https://newsapi.org/v1/articles?source=national-geographic&sortBy=top&apiKey=09fb3aeaa2a742fcb02dedb105bad7ae')
    elif newsType == "bbc":
    	response = urllib2.urlopen('https://newsapi.org/v1/articles?source=bbc-news&sortBy=top&apiKey=09fb3aeaa2a742fcb02dedb105bad7ae')
    elif newsType == "reddit":
    	response = urllib2.urlopen('https://newsapi.org/v1/articles?source=reddit-r-all&sortBy=top&apiKey=09fb3aeaa2a742fcb02dedb105bad7ae')
    elif newsType == "buzzfeed":
    	response = urllib2.urlopen('https://newsapi.org/v1/articles?source=buzzfeed&sortBy=top&apiKey=09fb3aeaa2a742fcb02dedb105bad7ae')
    elif newsType == "ign":
    	response = urllib2.urlopen('https://newsapi.org/v1/articles?source=ign&sortBy=top&apiKey=09fb3aeaa2a742fcb02dedb105bad7ae')
    elif newsType == "econ":
    	response = urllib2.urlopen('https://newsapi.org/v1/articles?source=the-economist&sortBy=top&apiKey=09fb3aeaa2a742fcb02dedb105bad7ae')
    else: 
    	return False;
    
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
              "url": data["articles"][2]["url"],
              "title": "Read more"
            }],
       	  },{
          	"title": data["articles"][3]["title"],
            "subtitle": data["articles"][3]["description"],
            "item_url": data["articles"][3]["url"],     
            "image_url": data["articles"][3]["urlToImage"],
            "buttons": [{
              "type": "web_url",
              "url": data["articles"][3]["url"],
              "title": "Read more"
            }],
       	  },{
          	"title": data["articles"][4]["title"],
            "subtitle": data["articles"][4]["description"],
            "item_url": data["articles"][4]["url"],     
            "image_url": data["articles"][4]["urlToImage"],
            "buttons": [{
              "type": "web_url",
              "url": data["articles"][4]["url"],
              "title": "Read more"
            }],
       	  },{
          	"title": data["articles"][5]["title"],
            "subtitle": data["articles"][5]["description"],
            "item_url": data["articles"][5]["url"],     
            "image_url": data["articles"][5]["urlToImage"],
            "buttons": [{
              "type": "web_url",
              "url": data["articles"][5]["url"],
              "title": "Read more"
            }],
       	  },{
          	"title": data["articles"][6]["title"],
            "subtitle": data["articles"][6]["description"],
            "item_url": data["articles"][6]["url"],     
            "image_url": data["articles"][6]["urlToImage"],
            "buttons": [{
              "type": "web_url",
              "url": data["articles"][6]["url"],
              "title": "Read more"
            }],
       	  },{
          	"title": data["articles"][7]["title"],
            "subtitle": data["articles"][7]["description"],
            "item_url": data["articles"][7]["url"],     
            "image_url": data["articles"][7]["urlToImage"],
            "buttons": [{
              "type": "web_url",
              "url": data["articles"][7]["url"],
              "title": "Read more"
            }],
       	  },{
          	"title": data["articles"][8]["title"],
            "subtitle": data["articles"][8]["description"],
            "item_url": data["articles"][8]["url"],     
            "image_url": data["articles"][8]["urlToImage"],
            "buttons": [{
              "type": "web_url",
              "url": data["articles"][8]["url"],
              "title": "Read more"
            }],
       	  },{
          	"title": data["articles"][9]["title"],
            "subtitle": data["articles"][9]["description"],
            "item_url": data["articles"][9]["url"],     
            "image_url": data["articles"][9]["urlToImage"],
            "buttons": [{
              "type": "web_url",
              "url": data["articles"][9]["url"],
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
