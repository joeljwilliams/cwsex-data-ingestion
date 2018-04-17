#!/usr/bin/env python3
from getpass import getpass
from os import environ

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

proxy_chan_id = 1151984662


session_name = environ.get('TG_SESSION', 'session')
user_phone = environ['TG_PHONE']
client = TelegramClient(
    session_name, int(environ['TG_API_ID']), environ['TG_API_HASH'],
    proxy=None, update_workers=4, spawn_read_thread=False
)

client.start()

@client.on(events.NewMessage(incoming=True, chats='cwsex'))
def message_handler(event):
    print(event)
    event.forward_to(proxy_chan_id)

client.idle()
