"""Bot main file"""


import os
import logging

# Third party integration
import requests
from slugify import slugify
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from telegram.error import BadRequest


BASE_API_URL = "https://hechizos.ordendelfenix.xyz/api"
NAME = "hechizoshlbot"
PORT = os.environ.get("PORT")
TOKEN = os.environ.get("TOKEN")


def reply(message, update):
    """Reply with a message"""
    update.message.reply_text(
        text=message, parse_mode=ParseMode.MARKDOWN, reply_to_message_id=None
    )


def get_spell(spell):
    """
    Get spell from API
    """
    url = f"{BASE_API_URL}/spells/{spell}"

    get_spell = requests.get(url)
    spells = get_spell.json()
    message = ""
    try:
        range_spell = (
            ", ".join([single_range["name"] for single_range in spells["range"]])
            or "Sin Rango"
        )
        wand = spells["object"]
        spell_type = spells["type"]
        method = spells["method"]
        description = spells["description"]

        message = f"""*{spell.title().replace("-", " ")}:*\n\n(*{range_spell}* - {wand}) Es *{spell_type}* y *{method}*:
                    \n{description}"""
    except KeyError:
        message = "El hechizo no existe"
    except BadRequest:
        message = "Creo que estás haciendo algo mal"

    return message


def get_range(range):
    """
    Respond with the /rango command
    """
    url = f"{BASE_API_URL}/range/{range}"

    response = requests.get(url)
    spells = response.json()
    message = ""
    try:
        spells_name = (
            ", ".join([s["name"] for s in spells]) or "No hay hechizos para ese rango"
        )
        message = f'*{range.title().replace("-", " ")}:*\n\n{spells_name}'
    except KeyError:
        message = "Probablemente ese rango no existe"
    return message


def start(bot, update):
    """
    Respond with the /start command
    """
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Hola, ahora puedes preguntar por algunos hechizos",
    )


# Commands to the bot responds


def spell(bot, update):
    """
    Respond with the /hechizo command
    """
    message = slugify(update.message.text)
    selected_spell = message[8:]
    reply(message=get_spell(selected_spell), update=update)


def _range(bot, update):
    """
    Respond with the /range command
    """
    message = slugify(update.message.text)
    selected_range = message[6:]
    reply(message=get_range(selected_range), update=update)


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    updater = Updater(token=TOKEN)

    dispatcher = updater.dispatcher

    start_handler = CommandHandler("iniciar", start)
    spell_handler = CommandHandler("hechizo", spell)
    range_handler = CommandHandler("rango", _range)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(spell_handler)
    dispatcher.add_handler(range_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
