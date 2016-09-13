import tweepy
import time
import schedule
import configparser
import smart_fact_crawler as sfc
from datetime import datetime
from functools import partial

config = configparser.ConfigParser()
config.read('auth.ini')

auth = tweepy.OAuthHandler(config['AUTH']['auth_token'],config['AUTH']['auth_secret'])
auth.set_access_token(config['AUTH']['access_token'],config['AUTH']['access_secret'])

api = tweepy.API(auth)

IDLE='Idle'
DATA='data'

state = {
    'source': None,
    'mcp_state' : IDLE,
    'timestamp' : None,
    'end_of_day' : None,
    'start_of_day' : None,
}

def check_smartfact():
    global state

    d = datetime.utcnow()
    if d > state['end_of_day'] and d < state['start_of_day']:
        smf = sfc.SmartFact()

        current_source = smf.drive()['tracking']['Source_Name']
        current_timestamp = smf.sun()['Time_Stamp']
        current_mcp_state = smf.status()['MCP']

        if current_source != state['source'] and 'data' in current_mcp_state:
            print('FACT is now monitoring the source: {}'.format(current_source))

        state['source'] = current_source
        state['mcp_state'] = current_mcp_state
        state['timestamp'] = current_timestamp


def get_twillight_times():
    global state
    smf = sfc.SmartFact()
    end_time = smf.sun()['End_of_day_time']
    start_time = smf.sun()['Start_of_day_time']
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
