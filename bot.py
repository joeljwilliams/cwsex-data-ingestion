#!/usr/bin/env python3

import logging
import re
import os

from influxdb import InfluxDBClient

from telegram import Bot, Update, Chat, User, Message
from telegram.ext import Updater, MessageHandler
from telegram.ext.filters import Filters
from telegram.utils.helpers import to_timestamp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = os.getenv('TOKEN')
PROXY_CHAN = -1001151984662
CWSEX_CHAN = -1001351906858

HOST = 'localhost'
PORT = 8086
USER = 'root'
PASSWORD = 'root'
DBNAME = 'cwsex'

item_re = re.compile(r"(^.[\w\-']+(?: \w+)*).+(?:\/t_([\d\w]{2,3}))$\n(?:\s{2}(\d{1,4})💰 x (\d{1,4})pcs = \d{1,4}💰\s)+", re.MULTILINE)
trade_re = re.compile(r"^(?:\s{2}(\d{1,4})💰 x (\d{1,4})pcs = \d{1,4}💰\s)", re.MULTILINE)

client = InfluxDBClient(HOST, PORT, USER, PASSWORD, DBNAME)


def error_cb(bot: Bot, update: Update, error: Exception):
    logger.exception(error)


def process_trade(bot: Bot, update: Update):
    chat = update.effective_chat # type: Chat
    user = update.effective_user # type: User
    msg = update.effective_message # type: Message

    if msg.forward_from_chat.id != CWSEX_CHAN:
        return

    logger.info('Processing trades for {:%d %B %Y %H:%M:%S}'.format(msg.forward_date))
    logger.debug('Received message: %s', msg.text)

    timestamp = to_timestamp(msg.forward_date)
    points = []

    for trades in re.finditer(item_re, msg.text):
        offset = 0
        logger.debug(trades.group(1,0))
        item, trade_text = trades.group(1, 0)
        measurement = item.replace(' ', r'\ ')
        step = 60//sum(1 for _ in trade_re.finditer(trade_text))
        for trade in re.finditer(trade_re, trade_text):
            logger.debug(trade.group(1,2))
            price, vol = trade.group(1,2)
            data = "{} price={},volume={} {}".format(measurement, price, vol, timestamp+offset)
            logger.info("writing to influxdb <%s>", data)
            offset += step
            points.append(data)
    
    ret = client.write_points(points, time_precision='s', protocol='line')
    if ret:
        logger.info("db written successfully")
    else:
        logger.error("failed writing points to db")


def main():
    ud = Updater(TOKEN)
    dp = ud.dispatcher

    dp.add_handler(MessageHandler(Filters.chat(chat_id=PROXY_CHAN), process_trade))

    dp.add_error_handler(error_cb)

    ud.start_polling()
    ud.idle()


if __name__ == '__main__':
    main()
