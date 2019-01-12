import json
import logging
import os
import re

from trendytom.traders.bitmex_trader import Bitmex

BITMEX_API_KEY = os.environ['BITMEX_API_KEY']
BITMEX_API_SECRET = os.environ['BITMEX_API_SECRET']
USE_TEST_NET = json.loads(os.environ['USE_TEST_NET'])
LEVERAGE_MULTIPLIER = float(os.environ['LEVERAGE_MULTIPLIER'])
STOP_LOSS_PERCENTAGE = float(os.environ['STOP_LOSS_PERCENTAGE'])

EMAIL_WHITELIST = os.environ['EMAIL_WHITELIST'].replace(' ', '').split(',')
GO_LONG_SUBJECT = os.environ['GO_LONG_SUBJECT']
GO_SHORT_SUBJECT = os.environ['GO_SHORT_SUBJECT']
ALLOWED_SUBJECTS = [GO_LONG_SUBJECT, GO_SHORT_SUBJECT]

def lambda_handler(event, context):
    
    client = Bitmex(BITMEX_API_KEY, BITMEX_API_SECRET, USE_TEST_NET,
                LEVERAGE_MULTIPLIER, STOP_LOSS_PERCENTAGE)

    email_subject = event['Records'][0]['ses']['mail']['commonHeaders']['subject']
    email_from = event['Records'][0]['ses']['mail']['commonHeaders']['from'][0]

    capture_group = re.search("(?P<name>.*) <(?P<email>.*)>", email_from)
    if not capture_group:
        logging.info(f'Email received with invalid from line. from={email_from} subject={email_subject}')
        exit(1)
        
    from_dict = capture_group.groupdict()
    email = from_dict['email']

    if (email not in EMAIL_WHITELIST) or (email_subject not in ALLOWED_SUBJECTS):
        logging.info(f'Email received with invalid from or subject line. from={email} subject={email_subject}')
        exit(1)

    position = client.get_current_position()

    if email_subject == GO_LONG_SUBJECT and not client.is_going_long():
        result = client.go_long()
        logging.info(f'Went long: {result}')
    elif email_subject == GO_SHORT_SUBJECT and not client.is_going_short():
        result = client.go_short()
        logging.info(f'Went short: {result}')