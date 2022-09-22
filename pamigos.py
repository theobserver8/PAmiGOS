# -*- coding: utf-8 -*-
import errno
import telebot
from time import sleep
from os import remove
from telebot.types import ReplyKeyboardMarkup, ForceReply, ReplyKeyboardRemove
import json, os

with open('config.json', 'r') as file:  config = json.load(file)

BOT_TOKEN = config['TOKEN']['PAmiGOSbot']

BOT_INTERVAL = 1
BOT_TIMEOUT = 20

#directorioRaiz = '/Users/ingen/Documents/RepoGitK/PAmiGOS/'
directorioRaiz = '/home/ec2-user/'
dicc_borrado_evento = {}

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
def showButtons(bot, chatid):
    botones = ReplyKeyboardMarkup(resize_keyboard=True)
    botones.row('/AYUDA❓')
    botones.row('/📝EVENTO📝', '/💰GASTOS💰')
    botones.row('/🚶🏼‍♂️AMIGOS🚶🏻‍♀️', '/💶CALCULAR💶')
    botones.row('/▪️OCULTAR_BOTONES▪️')
    msg = bot.send_message(chatid, 'Selecciona una opción:', reply_markup=botones)
    #return msg

def listar_eventos(chatid):
    contenido = os.listdir(directorioRaiz + 'BBDD/') #Guardo en una lista los archivos de la BBDD
    listado = []
    for filename in contenido:
        if filename.startswith(str(chatid) + '_'):
            nombreExtension = (filename.split('_', 1))[1] #Quito el chat id
            nombre = nombreExtension[:-5] #Quito la extensión .json
            listado.append(nombre)
    return listado
#--------------------------------------------------------------------------------------------------
def botactions(bot):
    @bot.message_handler(commands=['start'])
    def cmd_start(message):
        botones = ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Usa el comando /inicio para empezar', reply_markup=botones)

    @bot.message_handler(commands=['inicio', 'botones', 'CANCELAR'])
    def cmd_iniciar(message):
        showButtons(bot, message.chat.id)

    @bot.message_handler(commands=['AYUDA❓'])
    def cmd_help(message):
        botones = ReplyKeyboardRemove()
        texto = '<b>📝 <u>EVENTO</u> 📝</b>: Nombre del evento organizado.\nEjemplo: Viaje a Madrid.'
        texto += '\n\n<b>💰 <u>GASTOS</u> 💰</b>: Distintos gastos del evento.\nEjemplo: Alojamiento, gasolina, entradas, comida...'
        texto += '\n\n<b>🚶🏼‍♂️ <u>AMIGOS</u> 🚶🏻‍♀️</b>: Amigos que pueden formar parte de ese evento.'
        texto += '\n\n<b>💶 <u>CALCULAR</u> 💶</b>: Muestra los pagos a realizar entre vosotros para ajustar las cuentas.'
        texto += '\n\nUsa este comando /inicio para empezar...'
        bot.send_message(message.chat.id, texto, parse_mode="html", reply_markup=botones)


    @bot.message_handler(commands=['📝EVENTO📝'])
    def cmd_cuentas(message):
        botones = ReplyKeyboardMarkup(resize_keyboard=True)
        botones.row('/NUEVOevento', '/VEReventos')
        botones.row('/BORRARevento', '/CANCELAR')
        bot.send_message(message.chat.id, '__Editor de *EVENTOS*__\nEscoge una opción:', parse_mode="MarkdownV2", reply_markup=botones)

    @bot.message_handler(commands=['NUEVOevento'])
    def nuevo_evento(message):
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Vas a crear un nuevo evento.\nIntroduce el nombre:', reply_markup=markup)
        bot.register_next_step_handler(msg, crear_archivo)

    def crear_archivo(message):
        nombre = str(message.chat.id) + '_' + str(message.text)
        extension = '.json'
        path = directorioRaiz + '/BBDD/' + nombre + extension #Tengo previamente una carpeta BBDD que almacena los EVENTOS
        try:
            open(path, "x")
            bot.send_message(message.chat.id, 'Evento <b>' + str(message.text) + '</b> creado!', parse_mode="html")
        except:
            bot.send_message(message.chat.id, 'Ya existe ese evento.')
        showButtons(bot, message.chat.id)

    @bot.message_handler(commands=['VEReventos'])
    def ver_eventos(message):
        listado = listar_eventos(message.chat.id)
        if len(listado):
            listado_lineas = ('\n - '.join(listado)) #Listado separado en líneas
            bot.send_message(message.chat.id, '<b>La lista de eventos es:</b>\n ' + '- ' + listado_lineas, parse_mode="html")
        else:
            bot.send_message(message.chat.id, '<b>La lista de eventos está vacia!</b>', parse_mode="html")
        showButtons(bot, message.chat.id)

    @bot.message_handler(commands=['BORRARevento'])
    def borrar_evento(message):
        lista = listar_eventos(message.chat.id)
        if len(lista):
            botones = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(lista)
            if long_list%2 == 0:
                for n in range(0, long_list, 2):
                    botones.add(lista[n], lista[n+1])
            else:
                for n in range(0, long_list-1, 2):
                    botones.add(lista[n], lista[n+1])
                botones.add(lista[long_list-1])
            msg = bot.send_message(message.chat.id, 'Selecciona el evento a borrar:', reply_markup=botones)
            bot.register_next_step_handler(msg, dialog_borrar_evento)
        else:
            msg = bot.send_message(message.chat.id, '<b>La lista de eventos está vacia.\nNada que borrar.</b>', parse_mode="html")
            showButtons(bot, message.chat.id)
    
    def dialog_borrar_evento(message):
        dicc_borrado_evento[message.chat.id] = message.text
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('CONFIRMAR')
        markup.row('CANCELAR')
        msg = bot.send_message(message.chat.id, 'Confirma para borrar: <b>' + message.text + '</b>', parse_mode="html", reply_markup=markup)
        bot.register_next_step_handler(msg, borrado_final_evento)
    
    def borrado_final_evento(message):
        if message.text == 'CONFIRMAR':
            filename = str(message.chat.id) + '_' + dicc_borrado_evento[message.chat.id] + '.json'
            path = directorioRaiz + '/BBDD/' + filename
            remove(path)
            bot.send_message(message.chat.id, 'Elemento <b>' + dicc_borrado_evento[message.chat.id] + '</b> borrado!', parse_mode="html")
            del dicc_borrado_evento[message.chat.id]
        showButtons(bot, message.chat.id) #Los botones se van a mostrar luego sea la opción que sea


    @bot.message_handler(commands=['💰GASTOS💰'])
    def cmd_eventos(message):
        botones = ReplyKeyboardMarkup(resize_keyboard=True)
        botones.row('/NUEVOgasto', '/VERgastos')
        botones.row('/BORRARgasto', '/CANCELAR')
        bot.send_message(message.chat.id, '__Editor de *GASTOS*__\nEscoge una opción:', parse_mode="MarkdownV2", reply_markup=botones)

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