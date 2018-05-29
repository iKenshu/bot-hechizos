import os
import logging
import requests

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def get_spell(spell):
    url = 'http://hechizos.herokuapp.com/api/spells/' + spell

    get_spell = requests.get(url)
    spells = get_spell.json()
    message = f"""Es *{spells['type']}* y *{spells['object']}*. *({spells['range'][0]['name']})*:
                \n{spells['description']}
                """
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
    message = update.message.text.split(' ')
    print(len(message))
    spell = message[1]
    update.message.reply_text(text=get_spell(spell),
                              parse_mode=ParseMode.MARKDOWN)


def main():
    # update_spells = telegram.Bot()
    updater = Updater(token=os.environ['TOKEN'])
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    spell_handler = CommandHandler('hechizo', spell)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(spell_handler)

    updater.start_polling()


if __name__ == '__main__':
    main()
