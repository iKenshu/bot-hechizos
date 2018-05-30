# -*- coding: utf-8 -*-

import os
import logging
import requests

from slugify import slugify
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from telegram.error import BadRequest


def get_spell(spell):
    url = 'http://hechizos.herokuapp.com/api/spells/' + spell

    get_spell = requests.get(url)
    spells = get_spell.json()
    message = f"""(*{spells['range'][0]['name']}*) Es *{spells['type']}* y *{spells['method']}*.:
                \n{spells['description']}
                \n{spells['object']}"""
    return message


def get_range(range):
    url = 'http://hechizos.herokuapp.com/api/range/' + range

    get_spell = requests.get(url)
    ranges = get_spell.json()
    spell_name = []
    for spell in ranges:
        spell_name.append(spell['name'])
    message_format = ', '.join(spell_name)
    message = f'{message_format}'
    return message


def start(bot, update):
    """
    Respond with the /start command
    """
    bot.send_message(chat_id=update.message.chat_id,
                     text='Hola, ahora puedes preguntar por algunos hechizos')


def spell(bot, update):
    """
    Respond with the /hechizo command
    """
    message = slugify(update.message.text)
    spell = message[8:]
    try:
        update.message.reply_text(text=get_spell(spell),
                                  parse_mode=ParseMode.MARKDOWN)
    except BadRequest:
        update.message.reply_text(text='Creo que estás haciendo algo mal')


def range(bot, update):
    """
    Respond with the /range command
    """
    message = slugify(update.message.text)
    range = message[6:]
    update.message.reply_text(text=get_range(range),
                              parse_mode=ParseMode.MARKDOWN)


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    NAME = 'hechizoshlbot'
    PORT = os.environ.get('PORT')
    TOKEN = os.environ.get('TOKEN')

    updater = Updater(token=TOKEN)

    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    spell_handler = CommandHandler('hechizo', spell)
    range_handler = CommandHandler('rango', range)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(spell_handler)
    dispatcher.add_handler(range_handler)

    updater.start_webhook(listen='0.0.0.0',
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook(f'https://{NAME}.herokuapp.com/{TOKEN}')

    updater.start_polling()


if __name__ == '__main__':
    main()
