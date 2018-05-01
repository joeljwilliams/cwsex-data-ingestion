#!/usr/bin/env python3
from os import environ

from telethon import TelegramClient, events
from alchemysession import AlchemySessionContainer

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

proxy_chan_id = 1151984662

container = AlchemySessionContainer(environ['DATABASE_URL'])
session_name = environ.get('TG_SESSION', 'session')
session = container.new_session(session_name)

user_phone = environ['TG_PHONE']
client = TelegramClient(
    session, int(environ['TG_API_ID']), environ['TG_API_HASH'],
    proxy=None, update_workers=4, spawn_read_thread=False
)


def code_cb():
    return environ['TG_CODE']


client.start(phone=user_phone, code_callback=code_cb)


@client.on(events.NewMessage(incoming=True, chats='cwsex'))
def message_handler(event):
    print(event)
    event.forward_to(proxy_chan_id)


client.idle()
