"""Bot main file"""


import os
import logging
import re
import html

# Third party integration
import requests
from slugify import slugify
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from telegram.error import BadRequest


# BASE_API_URL = "https://hechizos.ordendelfenix.xyz/api"
BASE_API_URL = os.environ.get("API_HECHIZOS")
API_CHARACTERS = os.environ.get("API_CHARACTERS")
NAME = "hechizoshlbot"
PORT = os.environ.get("PORT")
TOKEN = os.environ.get("TOKEN")


def reply(message, update):
    """Reply with a message"""
    update.message.reply_text(
        text=html.unescape(message),
        parse_mode=ParseMode.MARKDOWN,
        reply_to_message_id=None,
    )


def get_patronus(patronus_search):
    """
    Get characters from API
    """
    if patronus_search[0:6] == "animal":
        url = f"{API_CHARACTERS}/characters/?search={patronus_search[7:]}"
    else:
        url = f"{API_CHARACTERS}/characters/{slugify(patronus_search)}"
    result = requests.get(url)
    result_data = list()
    if result.status_code == 200:
        data = result.json()
        check_results = data.get("results", False)
        if check_results and data["results"]:
            for character in data["results"]:
                result_data.append(
                    {"nick": f'{character["nick"]}:', "patronus": character["patronus"]}
                )
        check_url = data.get("url", False)
        if check_url:
            character = data
            result_data.append(
                {"nick": f'{character["nick"]}:', "patronus": character["patronus"]}
            )
    if not result_data:
        result_data.append(
            {"nick": "No se encontraron personajes con ese patronus", "patronus": ""}
        )
    return result_data


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


def get_initial_message():
    message = f"Hola, ahora puedes preguntar por algunos hechizos y cosas bonis de la ODF.\n\n"
    message = f"{message} *Comandos:* \n\n"
    message = f"{message}/iniciar: Iniciar el bot\n"
    message = f"{message}/help|ayuda|aiuda: Perdir aiuda\n"
    message = f"{message}/hechizo xxxx: Busca un hechizo por el nombre\n"
    message = f"{message}/rango xxxx: Busca los hechizos de un rango\n"
    message = f"{message}/patronus xxxx: Busca el patronus de un usuario\n"
    message = (
        f"{message}/patronus animal xxxx: Busca los usuarios que tengan ese patronus"
    )
    return message


def help_function(bot, update):
    reply(message=get_initial_message(), update=update)


def start(bot, update):
    """
    Respond with the /start command
    """

    bot.send_message(
        chat_id=update.message.chat_id, text=get_initial_message,
    )


# Commands to the bot responds


def patronus(bot, update):
    """
    Respond with the /patronus command
    """
    message = update.message.text
    search_term = message[10:]
    results = get_patronus(search_term)
    for character in results:
        message = f'*{character["nick"]}* {character["patronus"]}'
        reply(message=re.sub("<[^<]+?>", "", message), update=update)


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
    spell_handler = CommandHandler("patronus", patronus)
    spell_handler = CommandHandler("ayuda", help_function)
    spell_handler = CommandHandler("help", help_function)
    spell_handler = CommandHandler("aiuda", help_function)
    range_handler = CommandHandler("rango", _range)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(spell_handler)
    dispatcher.add_handler(range_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
