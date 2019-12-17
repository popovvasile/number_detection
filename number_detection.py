#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
from phonenumbers.phonenumberutil import region_code_for_number

import phonenumbers
import pycountry

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

HANDLE_DECISION, HANDLE_NUMBER = range(2)


def start(update, context):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="Verifică numărul", callback_data="check_number")]])
    update.message.reply_text(
        text='Salut! Eu sunt NumberBot! '
             'Sunt aici ca să ajut oamenii să depisteze operatorul sau țara unui număr de telefon. \n'
             'Ca să verifici un număr de telefon, apasă butonul de mai jos',
        reply_markup=keyboard)

    return ConversationHandler.END


def ask_operator_or_country(update, context):
    message = update.callback_query.message
    context.bot.delete_message(chat_id=message.chat_id,
                               message_id=message.message_id)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="Țara", callback_data="want_country")],
                                     [InlineKeyboardButton(text="Operator", callback_data="want_operator")],
                                     [InlineKeyboardButton(text="STOP", callback_data="stop")]])

    reply_markup = keyboard
    message.reply_text('Vreți să depistați operatorul sau țara acestui număr de telefon? \n'
                       'Pot depista numai operatorii din Republica Moldova ',
                       reply_markup=reply_markup)
    return HANDLE_DECISION


def handle_operator_or_country(update, context):
    message = update.callback_query.message
    context.bot.delete_message(chat_id=message.chat_id,
                               message_id=message.message_id)
    context.user_data["decision"] = update.callback_query.data
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="STOP", callback_data="stop")]])
    message.reply_text('Introduceți numărul de telefon. Apăsați butonul STOP dacă vreți să opriți comanda. ',
                       reply_markup=keyboard)

    return HANDLE_NUMBER


def handle_number(update, context):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="Verifică alt număr", callback_data="check_number")]])

    if context.user_data["decision"] == "want_country":
        pn = phonenumbers.parse(update.message.text)
        country = pycountry.countries.get(alpha_2=region_code_for_number(pn)).name
        update.message.reply_text('Numărul {} este din țara: {}'.format(update.message.text,
                                                                        country),
                                  reply_markup=keyboard)
        return ConversationHandler.END
    elif context.user_data["decision"] == "want_operator":
        operators_dict = {"060": "Orange",
                          "061": "Orange",
                          "062": "Orange",
                          "068": "Orange",
                          "069": "Orange",
                          "066": "Unite",
                          "067": "Unite",
                          "078": "Moldcell",
                          "079": "Moldcell",
                          }
        operator = operators_dict.get(update.message.text[:3])
        update.message.reply_text('Numărul {} aparatine operatorului: {}'.format(update.message.text,
                                                                                 operator),
                                  reply_markup=keyboard)
        return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text('Bye! I hope we can talk again some day.')
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("1028868185:AAGs9Sown6LRgkTT0ImW93mi_refQbn83W8", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    rex_help_handler = MessageHandler(Filters.regex(r"^((?!@).)*$"), start)  # catch all messages
    start_handler = CommandHandler('start', start)  # catch the /start message

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(pattern='check_number', callback=ask_operator_or_country)],

        states={
            HANDLE_DECISION: [CallbackQueryHandler(pattern='want_', callback=handle_operator_or_country)],
            HANDLE_NUMBER: [MessageHandler(Filters.text, handle_number)],
        },

        fallbacks=[CallbackQueryHandler(pattern='stop', callback=cancel)]
    )

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(conv_handler)
    # log all errors
    # dispatcher.add_error_handler(error)
    dispatcher.add_handler(rex_help_handler)  # Trebuie sa fie la urma, ultimul din toti "handlers"

    # Start the Bot
    updater.start_polling(timeout=60, read_latency=60, clean=True, bootstrap_retries=5)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
