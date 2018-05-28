import os
import logging
import requests
import telegram

from telegram.ext import Updater, CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


bot_spells = telegram.Bot(token=os.environ['TOKEN'])
updater = Updater(bot_spells.token)
dispatcher = updater.dispatcher


def get_spell(spell):
    url = 'http://hechizos.herokuapp.com/api/spells/' + spell

    get_spell = requests.get(url)
    spells = get_spell.json()
    return spells['description']


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
    message = update.message.text.split(' ')
    spell = message[1]
    bot.send_message(chat_id=update.message.chat_id,
                     text=get_spell(spell))


start_handler = CommandHandler('start', start)
spell_handler = CommandHandler('hechizo', spell)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(spell_handler)

updater.start_polling()
