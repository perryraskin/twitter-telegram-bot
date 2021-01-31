import requests
import os
import json
import logging
import time
from datetime import datetime
from types import SimpleNamespace
from dotenv import load_dotenv
load_dotenv()

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(text):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + text

    response = requests.get(send_text)
    logger.info('Message sent to chatID ' + chat_id)

    return response.json()

def config_logger():
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    logger.addHandler(handler)

def auth():
    return os.getenv("TWITTER_BEARER_TOKEN")


def create_url():
    # Replace with user ID below
    user_id = 42980370 #@9to5Toys
    return "https://api.twitter.com/2/users/{}/tweets?max_results=5".format(user_id)


def get_params():
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    return {"tweet.fields": "created_at"}


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers, params):
    response = requests.request("GET", url, headers=headers, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def main():
    try:
        config_logger()
        bearer_token = auth()
        url = create_url()
        headers = create_headers(bearer_token)
        params = get_params()
        
        while True:
            logger.info('Checking latest tweet...')
            json_response = connect_to_endpoint(url, headers, params)
            json_string = json.dumps(json_response, indent=4, sort_keys=True)
            #print(json.dumps(json_response, indent=4, sort_keys=True))
            json_object = json.loads(json_string, object_hook=lambda d: SimpleNamespace(**d))
            tweet = json_object.data[0]
            # print(tweet.created_at)
            # print(tweet.id)
            # print(tweet.text)

            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            tweet_datetime = tweet.created_at[0:10] + " " + tweet.created_at[12:16]
            
            print("Current Date & Time:", now)
            print("Tweet Date & Time:", tweet_datetime)

            #send the tweet as a Telegram message if it was
            #tweeted in the current minute
            if now == tweet_datetime:
                send_telegram(tweet.text)
            
            logger.info('Sleeping for 60 seconds')
            time.sleep(60)
    
    except Exception as error:
        bot_message = "Error in ToysDeals Bot: " + str(error)
        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + bot_message
        response = requests.get(send_text)


if __name__ == "__main__":
    main()