# -*- coding: utf-8 -*-
import telebot
from time import sleep
from telebot.types import ReplyKeyboardMarkup
from telebot.types import ForceReply
from telebot.types import ReplyKeyboardRemove
import json

with open('config.json', 'r') as file:  config = json.load(file)

BOT_TOKEN = config['TOKEN']['PAmiGOSbot']

BOT_INTERVAL = 1
BOT_TIMEOUT = 20

DEBUG = True

def bot_polling():
    print("Starting bot polling now")

    while True:
        try:
            print("New bot instance started")
            bot = telebot.TeleBot(BOT_TOKEN)
            botactions(bot)
            bot.set_my_commands([
                telebot.types.BotCommand('/botones', 'Muestra los botones'),
            ])
            bot.polling(none_stop=True, interval=BOT_INTERVAL, timeout=BOT_TIMEOUT)

        except Exception as ex:
            print("Bot polling failed, restarting in {}sec. Error:\n{}".format(BOT_TIMEOUT, ex))
            bot.stop_polling()
            sleep(BOT_TIMEOUT)

        else:
            bot.stop_polling()
            print("Bot polling loop finished")
            break
#--------------------------------------------------------------------------------------------------
def botactions(bot):
    @bot.message_handler(commands=['start'])
    def cmd_start(message):
        botones = ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Usa el comando /inicio para empezar', reply_markup=botones)

    @bot.message_handler(commands=['inicio', 'botones', 'CANCELAR'])
    def cmd_iniciar(message):
        botones = ReplyKeyboardMarkup(resize_keyboard=True)
        botones.row('/AYUDA❓')
        botones.row('/📝EVENTO📝', '/💰GASTOS💰')
        botones.row('/🚶🏼‍♂️AMIGOS🚶🏻‍♀️', '/💶CALCULAR💶')
        botones.row('/▪️OCULTAR_BOTONES▪️')
        msg = bot.send_message(message.chat.id, "Elige una opción:", reply_markup=botones)

    @bot.message_handler(commands=['AYUDA❓'])
    def cmd_help(message):
        botones = ReplyKeyboardRemove()
        texto = '<b>📝 <u>EVENTO</u> 📝</b>: Nombre del evento organizado.\nEjemplo: Viaje a Madrid.'
        texto += '\n\n<b>💰 <u>GASTOS</u> 💰</b>: Distintos gastos del evento.\nEjemplo: Alojamiento, gasolina, entradas, comida...'
        texto += '\n\n<b>🚶🏼‍♂️ <u>AMIGOS</u> 🚶🏻‍♀️</b>: Amigos que pueden formar parte de ese evento.'
        texto += '\n\n<b>💶 <u>CALCULAR</u> 💶</b>: Muestra los pagos a realizar entre vosotros para ajustar las cuentas.'
        texto += '\n\nUsa este comando /inicio para empezar...'
        msg = bot.send_message(message.chat.id, texto, parse_mode="html", reply_markup=botones)

    @bot.message_handler(commands=['📝EVENTO📝'])
    def cmd_cuentas(message):
        botones = ReplyKeyboardMarkup(resize_keyboard=True)
        botones.row('/NUEVOevento', '/VEReventos')
        botones.row('/BORRARevento', '/CANCELAR')
        bot.send_message(message.chat.id, '__Editor de *CUENTAS*__\nEscoge una opción:', parse_mode="MarkdownV2", reply_markup=botones)

    @bot.message_handler(commands=['💰GASTOS💰'])
    def cmd_eventos(message):
        botones = ReplyKeyboardMarkup(resize_keyboard=True)
        botones.row('/NUEVOgasto', '/VERgastos')
        botones.row('/BORRARgasto', '/CANCELAR')
        bot.send_message(message.chat.id, '__Editor de *EVENTOS*__\nEscoge una opción:', parse_mode="MarkdownV2", reply_markup=botones)

    @bot.message_handler(commands=['🚶🏼‍♂️AMIGOS🚶🏻‍♀️'])
    def cmd_amigos(message):
        botones = ReplyKeyboardMarkup(resize_keyboard=True)
        botones.row('/NUEVOamigo', '/VERamigos')
        botones.row('/BORRARamigo', '/CANCELAR')
        bot.send_message(message.chat.id, '__Editor de *AMIGOS*__\nEscoge una opción:', parse_mode="MarkdownV2", reply_markup=botones)

    @bot.message_handler(commands=['💶CALCULAR💶'])
    def cmd_calcular(message):
        botones = ReplyKeyboardMarkup(resize_keyboard=True)
        botones.row('/CALCULAR')
        botones.row('/CANCELAR')
        bot.send_message(message.chat.id, 'Confirma el cálculo de la cuenta y mostraré los distintos pagos a realizar.', reply_markup=botones)

    @bot.message_handler(commands=['▪️OCULTAR_BOTONES▪️'])
    def cmd_hideButtons(message):
        botones = ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Botones ocultos.\nUsa el botón menú o el comando /inicio para volver a mostrarlos.', reply_markup=botones)
#--------------------------------------------------------------------------------------------------
bot_polling()