import tweepy
import time
import schedule
import configparser
import smart_fact_crawler as sfc
from datetime import datetime

config = configparser.ConfigParser()
config.read('auth.ini')

auth = tweepy.OAuthHandler(config['AUTH']['auth_token'], config['AUTH']['auth_secret'])
auth.set_access_token(config['AUTH']['access_token'], config['AUTH']['access_secret'])

api = tweepy.API(auth)

IDLE = 'Idle'
DATA = 'data'

state = {
    'source': None,
    'mcp_state': IDLE,
    'end_of_day': None,
    'start_of_day': None,
}


def check_smartfact():
    global state

    d = datetime.utcnow()
    if d > state['end_of_day'] and d < state['start_of_day']:

        current_source = sfc.tracking().source_name
        current_mcp_state = sfc.status().mcp

        if current_source != state['source'] and 'data' in current_mcp_state:
            print('FACT is now monitoring the source: {}'.format(current_source))

        state['source'] = current_source
        state['mcp_state'] = current_mcp_state

    print(state)


def get_twillight_times():
    global state
    sun = sfc.sun()
    end_time = sun.end_of_day_time
    start_time = sun.start_of_day_time
    state['end_of_day'] = end_time
    state['start_of_day'] = start_time


def main():

    global state

    get_twillight_times()

    schedule.every(1).day.at('15:00').do(get_twillight_times)
    schedule.every(5).minutes.do(check_smartfact)

    while True:
        schedule.run_pending()
        time.sleep(10)


if __name__ == '__main__':
    main()
