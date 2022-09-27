# -*- coding: utf-8 -*-
from lib2to3.pygram import pattern_grammar
import telebot
from time import sleep
from os import remove
from telebot.types import ReplyKeyboardMarkup, ForceReply, ReplyKeyboardRemove
import json, os

with open('config.json', 'r') as file:  config = json.load(file)

BOT_TOKEN = config['TOKEN']['PAmiGOSbot']
DIRECTORIO_RAIZ = config['ROOT_PATH']

BOT_INTERVAL = 1
BOT_TIMEOUT = 20

dicc_temp = {}
dicc_temp['dicc_evento'] = {}
dicc_temp['amigos'] = {}
dicc_temp['dicc_amigo_temp'] = {}
dicc_temp['dicc_path'] = {}
dicc_temp['dicc_gasto'] = {}
dicc_temp['dicc_gasto_nuevo'] = {}
dicc_temp['num_gasto_borrar'] = {}
dicc_temp['calculo'] = {}
dicc_temp['listas'] = {}
dicc_data = {}
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
    botones.row('/☕️KO-FI☕️', '/AYUDA❓')
    botones.row('/📝EVENTO📝', '/💰GASTOS💰')
    botones.row('/🚶🏼‍♂️AMIGOS🚶🏻‍♀️', '/💶CALCULAR💶')
    botones.row('/▪️OCULTAR_BOTONES▪️')
    msg = bot.send_message(chatid, 'Selecciona una opción:', reply_markup=botones)
    #return msg

def agrupar_botones(long_list, lista, botones):
    if long_list%2 == 0:
        for n in range(0, long_list, 2):
            botones.add(lista[n], lista[n+1])
    else:
        for n in range(0, long_list-1, 2):
            botones.add(lista[n], lista[n+1])
        botones.add(lista[long_list-1])
    return botones

def createFilenameToPath(message):
    nombre = str(message.chat.id) + '_' + str(message.text)
    extension = '.json'
    path = DIRECTORIO_RAIZ + '/BBDD/' + nombre + extension #Tengo previamente una carpeta BBDD que almacena los EVENTOS
    return path

def filenameToPath(message):
    filename = str(message.chat.id) + '_' + dicc_temp['dicc_evento'][message.chat.id] + '.json'
    path = DIRECTORIO_RAIZ + '/BBDD/' + filename
    return path

def listar_eventos(chatid):
    contenido = os.listdir(DIRECTORIO_RAIZ + 'BBDD/') #Guardo en una lista los archivos de la BBDD
    listado = []
    for filename in contenido:
        if filename.startswith(str(chatid) + '_'):
            nombreExtension = (filename.split('_', 1))[1] #Quito el chat id
            nombre = nombreExtension[:-5] #Quito la extensión .json
            listado.append(nombre)
    return listado

def createList(n):
    lst = []
    for i in range(n):
        i = str(i+1)
        lst.append(i)
    return(lst)

def loadData(chatid, path):
    f = open(path) 
    datos = json.load(f)
    dicc_data[chatid] = datos
    f.close()

def saveData(chatid, path):
    with open(path, "w") as archivo:
        json.dump(dicc_data[chatid], archivo)
#--------------------------------------------------------------------------------------------------
def botactions(bot):
    
    @bot.message_handler(commands=['start'])
    def cmd_start(message):
        botones = ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Usa el comando /inicio para empezar', reply_markup=botones)

    @bot.message_handler(commands=['inicio', 'botones', 'CANCELAR'])
    def cmd_iniciar(message):
        showButtons(bot, message.chat.id)

    @bot.message_handler(commands=['☕️KO-FI☕️'])
    def cmd_kofi(message):
        texto = 'Si te ha gustado mi trabajo y te resulta útil, apoyando con un café ayudarás al desarrollo de PAmiGOS.\n'
        texto += '<a href= "https://ko-fi.com/theobserver8">https://ko-fi.com/theobserver8</a>'
        bot.send_message(message.chat.id, texto, parse_mode="html")

    @bot.message_handler(commands=['AYUDA❓'])
    def cmd_help(message):
        botones = ReplyKeyboardRemove()
        texto = '<b>📝 <u>EVENTO</u> 📝</b>: Nombre del evento organizado.\nEjemplo: Viaje a Madrid.'
        texto += '\n\n<b>💰 <u>GASTOS</u> 💰</b>: Distintos gastos del evento.\nEjemplo: Alojamiento, gasolina, entradas, comida...'
        texto += '\n\n<b>🚶🏼‍♂️ <u>AMIGOS</u> 🚶🏻‍♀️</b>: Amigos que pueden formar parte de ese evento. No es una mención, escribe su nombre directamente.'
        texto += '\n\n<b>💶 <u>CALCULAR</u> 💶</b>: Muestra los pagos a realizar entre vosotros para ajustar las cuentas.'
        texto += '\n\nUsa este comando /inicio para empezar...'
        bot.send_message(message.chat.id, texto, parse_mode="html", reply_markup=botones)


    @bot.message_handler(commands=['📝EVENTO📝'])
    def cmd_evento(message):
        botones = ReplyKeyboardMarkup(resize_keyboard=True)
        botones.row('/NUEVOevento', '/VEReventos')
        botones.row('/BORRARevento', '/CANCELAR')
        bot.send_message(message.chat.id, '__Editor de *EVENTOS*__\nEscoge una opción:', parse_mode="MarkdownV2", reply_markup=botones)

    @bot.message_handler(commands=['NUEVOevento'])
    def cmd_nuevoEvento(message):
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Vas a crear un nuevo evento.\nIntroduce el nombre:', reply_markup=markup)
        bot.register_next_step_handler(msg, crear_archivo)

    def crear_archivo(message):
        path = createFilenameToPath(message)
        try:
            archivo = open(path, "x")
            archivo.close()
            dicc = {}
            dicc['amigos'] = []
            dicc['gastos'] = []
            with open(path, "w") as iniciar_archivo:
                json.dump(dicc ,iniciar_archivo)
            bot.send_message(message.chat.id, 'Evento <b>' + str(message.text) + '</b> creado!', parse_mode="html")
        except:
            bot.send_message(message.chat.id, 'Ya existe ese evento.')
        showButtons(bot, message.chat.id)

    @bot.message_handler(commands=['VEReventos'])
    def cmd_verEventos(message):
        listado = listar_eventos(message.chat.id)
        if len(listado):
            listado_lineas = ('\n - '.join(listado)) #Listado separado en líneas
            bot.send_message(message.chat.id, '<b>La lista de eventos es:</b>\n ' + '- ' + listado_lineas, parse_mode="html")
        else:
            bot.send_message(message.chat.id, '<b>La lista de eventos está vacia!</b>', parse_mode="html")
        showButtons(bot, message.chat.id)

    @bot.message_handler(commands=['BORRARevento'])
    def cmd_borrarEvento(message):
        lista = listar_eventos(message.chat.id)
        if len(lista):
            eventos = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(lista)
            eventos = agrupar_botones(long_list, lista, eventos)
            msg = bot.send_message(message.chat.id, 'Selecciona el evento a borrar:', reply_markup=eventos)
            bot.register_next_step_handler(msg, dialogBorrarEvento)
        else:
            bot.send_message(message.chat.id, '<b>La lista de eventos está vacia.\nNada que borrar.</b>', parse_mode="html")
            showButtons(bot, message.chat.id)
    
    def dialogBorrarEvento(message):
        dicc_temp['dicc_evento'][message.chat.id] = message.text
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('CONFIRMAR')
        markup.row('CANCELAR')
        msg = bot.send_message(message.chat.id, 'Confirma para borrar: <b>' + message.text + '</b>', parse_mode="html", reply_markup=markup)
        bot.register_next_step_handler(msg, borradoFinalEvento)
    
    def borradoFinalEvento(message):
        if message.text == 'CONFIRMAR':
            path = filenameToPath(message)
            remove(path)
            bot.send_message(message.chat.id, 'Evento <b>' + dicc_temp['dicc_evento'][message.chat.id] + '</b> borrado!', parse_mode="html")
            del dicc_temp['dicc_evento'][message.chat.id]
        showButtons(bot, message.chat.id) #Los botones se van a mostrar luego sea la opción que sea


    @bot.message_handler(commands=['🚶🏼‍♂️AMIGOS🚶🏻‍♀️'])
    def cmd_amigos(message):
        botones = ReplyKeyboardMarkup(resize_keyboard=True)
        botones.row('/NUEVOamigo', '/VERamigos')
        botones.row('/BORRARamigo', '/CANCELAR')
        bot.send_message(message.chat.id, '__Editor de *AMIGOS*__\nEscoge una opción:', parse_mode="MarkdownV2", reply_markup=botones)

    @bot.message_handler(commands='NUEVOamigo')
    def cmd_nuevoAmigo(message):
        lista = listar_eventos(message.chat.id)
        if len(lista):
            eventos = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(lista)
            eventos = agrupar_botones(long_list, lista, eventos)
            msg = bot.send_message(message.chat.id, 'Selecciona el evento al que añadir amigos:', reply_markup=eventos)
            bot.register_next_step_handler(msg, nuevoAmigoEvento)
        else:
            bot.send_message(message.chat.id, '<b>No hay eventos para añadir amigos.\nCrea primero un evento.</b>', parse_mode="html")
            showButtons(bot, message.chat.id)
    
    def nuevoAmigoEvento(message):
        dicc_temp['dicc_evento'][message.chat.id] = message.text
        path = filenameToPath(message)
        loadData(message.chat.id, path)
        dicc_temp['dicc_path'][message.chat.id] = path
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Introduce el nombre del amigo:', reply_markup=markup)
        bot.register_next_step_handler(msg, leerAmigo)

    def leerAmigo(message):
        dicc_temp['dicc_amigo_temp'][message.chat.id] = message.text
        if message.text in dicc_data[message.chat.id]['amigos']:
            msg = bot.send_message(message.chat.id, '<b>Este nombre ya existe.\nIntroduce otro nombre:</b>', parse_mode="html")
            bot.register_next_step_handler(msg, leerAmigo)
        else:
            dicc_data[message.chat.id]['amigos'].append(dicc_temp['dicc_amigo_temp'][message.chat.id]) #Añado el amigo escrito al dicc de datos.
            bot.send_message(message.chat.id, 'Amigo <b>' + str(message.text) + '</b> añadido!', parse_mode="html")
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('NO', 'SI')
            msg = bot.send_message(message.chat.id, '¿Quieres añadir otro amigo?', reply_markup=markup)
            bot.register_next_step_handler(msg, dialogAddAmigo)

    def dialogAddAmigo(message):
        if message.text == 'SI':
            markup = ForceReply()
            msg = bot.send_message(message.chat.id, 'Introduce el nombre del amigo:', reply_markup=markup)
            bot.register_next_step_handler(msg, leerAmigo)
        else:
            saveData(message.chat.id, dicc_temp['dicc_path'][message.chat.id]) #Lo guardo en el archivo
            showButtons(bot, message.chat.id)

    @bot.message_handler(commands='VERamigos')
    def cmd_verAmigos(message):
        lista = listar_eventos(message.chat.id)
        if len(lista):
            eventos = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(lista)
            eventos = agrupar_botones(long_list, lista, eventos)
            msg = bot.send_message(message.chat.id, 'Selecciona evento para ver los amigos:', reply_markup=eventos)
            bot.register_next_step_handler(msg, verAmigosEvento)
        else:
            bot.send_message(message.chat.id, '<b>No hay eventos para añadir amigos.\nCrea primero un evento.</b>', parse_mode="html")
            showButtons(bot, message.chat.id)

    def verAmigosEvento(message):
        dicc_temp['dicc_evento'][message.chat.id] = message.text #Hay que añadir esta línea para que en la ruta del archivo se sepa el evento.
        path = filenameToPath(message)
        loadData(message.chat.id, path)
        listado = dicc_data[message.chat.id]['amigos']

        if len(listado):
            listado_lineas = ('\n - '.join(listado)) #Listado separado en líneas
            bot.send_message(message.chat.id, '<b>Lista de amigos:</b>\n ' + '- ' + listado_lineas, parse_mode="html")
        else:
            bot.send_message(message.chat.id, '<b>No hay ningún amigo en el evento!</b>', parse_mode="html")
        showButtons(bot, message.chat.id)

    @bot.message_handler(commands='BORRARamigo')
    def cmd_borrarAmigo(message):
        lista = listar_eventos(message.chat.id)
        if len(lista):
            eventos = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(lista)
            eventos = agrupar_botones(long_list, lista, eventos)
            msg = bot.send_message(message.chat.id, 'Selecciona evento para ver los amigos:', reply_markup=eventos)
            bot.register_next_step_handler(msg, borrarAmigosEvento)
        else:
            bot.send_message(message.chat.id, '<b>No hay eventos para borrar amigos.\nCrea primero un evento.</b>', parse_mode="html")
            showButtons(bot, message.chat.id)

    def borrarAmigosEvento(message):
        dicc_temp['dicc_evento'][message.chat.id] = message.text #Hay que añadir esta línea para que en la ruta del archivo se sepa el evento.
        path = filenameToPath(message)
        loadData(message.chat.id, path)
        dicc_temp['dicc_path'][message.chat.id] = path #Guardo la ruta, con el chat id. Para acceder luego al borrado del amigo.
        lista_amigos = dicc_data[message.chat.id]['amigos']
        if len(lista_amigos):
            botones = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(lista_amigos)
            botones = agrupar_botones(long_list, lista_amigos, botones)
            msg = bot.send_message(message.chat.id, 'Selecciona amigo a borrar:', reply_markup=botones)
            bot.register_next_step_handler(msg, dialogBorrarAmigo)
        else:
            bot.send_message(message.chat.id, '<b>No hay amigos para borrar en este evento.</b>', parse_mode="html")
            showButtons(bot, message.chat.id)

    def dialogBorrarAmigo(message):
        dicc_temp['dicc_amigo_temp'][message.chat.id] = message.text
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('CONFIRMAR')
        markup.row('CANCELAR')
        msg = bot.send_message(message.chat.id, 'Confirma para borrar: <b>' + message.text + '</b>', parse_mode="html", reply_markup=markup)
        bot.register_next_step_handler(msg, borradoFinalAmigo)
    
    def borradoFinalAmigo(message):
        if message.text == 'CONFIRMAR':
            dicc_data[message.chat.id]['amigos'].remove(dicc_temp['dicc_amigo_temp'][message.chat.id]) #Elimina amigo de la lista
            bot.send_message(message.chat.id, 'Amigo <b>' + dicc_temp['dicc_amigo_temp'][message.chat.id] + '</b> borrado!', parse_mode="html")
            saveData(message.chat.id, dicc_temp['dicc_path'][message.chat.id]) #Lo guardo en el archivo
        showButtons(bot, message.chat.id) #Los botones se van a mostrar luego sea la opción que sea


    @bot.message_handler(commands=['💰GASTOS💰'])
    def cmd_gastos(message):
        botones = ReplyKeyboardMarkup(resize_keyboard=True)
        botones.row('/NUEVOgasto', '/VERgastos')
        botones.row('/BORRARgasto', '/CANCELAR')
        bot.send_message(message.chat.id, '__Editor de *GASTOS*__\nEscoge una opción:', parse_mode="MarkdownV2", reply_markup=botones)

    @bot.message_handler(commands='NUEVOgasto')
    def cmd_nuevoGasto(message):
        lista = listar_eventos(message.chat.id)
        if len(lista):
            eventos = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(lista)
            eventos = agrupar_botones(long_list, lista, eventos)
            msg = bot.send_message(message.chat.id, 'Selecciona el evento al que añadir gastos:', reply_markup=eventos)
            bot.register_next_step_handler(msg, nuevoGastoEvento)
        else:
            bot.send_message(message.chat.id, '<b>No hay eventos para añadir gastos.\nCrea primero un evento.</b>', parse_mode="html")
            showButtons(bot, message.chat.id)

    def nuevoGastoEvento(message):
        dicc_temp['dicc_evento'][message.chat.id] = message.text
        path = filenameToPath(message)
        loadData(message.chat.id, path)
        listado = list(dicc_data[message.chat.id]['amigos']) #Hago una copia de la lista, porque sino modifico la original
        dicc_temp['dicc_path'][message.chat.id] = path
        dicc_temp['dicc_gasto'][message.chat.id] = {}
        dicc_temp['amigos'][message.chat.id] = listado
        if len(listado):
            amigos = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(listado)
            amigos = agrupar_botones(long_list, listado, amigos)
            msg = bot.send_message(message.chat.id, 'Quién ha pagado este gasto?', reply_markup=amigos)
            bot.register_next_step_handler(msg, leerPagadorPedirConcepto)
        else:
            bot.send_message(message.chat.id, '<b>No hay ningún amigo en el evento!</b>', parse_mode="html")
            showButtons(bot, message.chat.id)

    def leerPagadorPedirConcepto(message):
        dicc_temp['dicc_gasto'][message.chat.id]['pagador'] = message.text
        dicc_temp['amigos'][message.chat.id].remove(message.text) #Elimino al pagador del listado de amigos a aparecer
        dicc_temp['dicc_gasto'][message.chat.id]['participantes'] = [message.text] #Añado el pagador a los participantes
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Introduce el concepto del gasto:', reply_markup=markup)
        bot.register_next_step_handler(msg, leerConceptoPedirCantidad)

    def leerConceptoPedirCantidad(message):
        dicc_temp['dicc_gasto'][message.chat.id]['concepto'] = message.text
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Introduce la cantidad pagada:', reply_markup=markup)
        bot.register_next_step_handler(msg, leerCantidadPedirParticipantes)

    def leerCantidadPedirParticipantes(message):
        dicc_temp['dicc_gasto'][message.chat.id]['cantidad'] = message.text
        if not message.text.isdigit():
            msg = bot.send_message(message.chat.id, 'ERROR: La cantidad debe de ser un número.\nIntroduce la cantidad pagada:')
            bot.register_next_step_handler(msg, leerCantidadPedirParticipantes) #Volvemos a ejecutar esta función
        else:
            dicc_temp['amigos'][message.chat.id].append('FIN 🔚') #Añado un elemento llamado FIN
            participantes = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(dicc_temp['amigos'][message.chat.id])
            participantes = agrupar_botones(long_list, dicc_temp['amigos'][message.chat.id], participantes)
            msg = bot.send_message(message.chat.id, 'Selecciona los participantes:', reply_markup=participantes)
            bot.register_next_step_handler(msg, pedirParticipantesGuardarGasto)

    def pedirParticipantesGuardarGasto(message):
        if message.text == 'FIN 🔚':
            dicc_data[message.chat.id]['gastos'].append(dicc_temp['dicc_gasto'][message.chat.id])
            bot.send_message(message.chat.id, 'Gasto <b>' + dicc_temp['dicc_gasto'][message.chat.id]['concepto'] + '</b> añadido a ' + dicc_temp['dicc_evento'][message.chat.id] + '!', parse_mode="html")
            saveData(message.chat.id, dicc_temp['dicc_path'][message.chat.id]) #Lo guardo en el archivo
            showButtons(bot, message.chat.id)
        else:
            dicc_temp['dicc_gasto'][message.chat.id]['participantes'].append(message.text)
            dicc_temp['amigos'][message.chat.id].remove(message.text) #Quito de la lista amigo seleccionado
            participantes_restantes = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(dicc_temp['amigos'][message.chat.id]) #Vuelvo a mostrar el listado
            participantes_restantes = agrupar_botones(long_list, dicc_temp['amigos'][message.chat.id], participantes_restantes)
            msg = bot.send_message(message.chat.id, 'Selecciona los participantes:', reply_markup=participantes_restantes)
            bot.register_next_step_handler(msg, pedirParticipantesGuardarGasto) #Recurro a esta función

    @bot.message_handler(commands='VERgastos')
    def cmd_verGastos(message):
        lista = listar_eventos(message.chat.id)
        if len(lista):
            eventos = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(lista)
            eventos = agrupar_botones(long_list, lista, eventos)
            msg = bot.send_message(message.chat.id, 'Selecciona evento para ver los gastos:', reply_markup=eventos)
            bot.register_next_step_handler(msg, verGastosEvento)
        else:
            bot.send_message(message.chat.id, '<b>No hay eventos.\nCrea primero un evento.</b>', parse_mode="html")
            showButtons(bot, message.chat.id)

    def verGastosEvento(message):
        dicc_temp['dicc_evento'][message.chat.id] = message.text #Hay que añadir esta línea para que en la ruta del archivo se sepa el evento.
        path = filenameToPath(message)
        loadData(message.chat.id, path)
        listado = dicc_data[message.chat.id]['gastos']
        if len(listado):
            texto = ''
            for n in listado:
                texto += 'Evento nº' + str(listado.index(n)+1) + ':\n'
                texto += 'Pagador: ' + n['pagador'] + '\n'
                texto += 'Concepto: ' + n['concepto'] + '\n'
                texto += 'Cantidad: ' + str(n['cantidad']) + '\n'
                texto += 'Participantes: '
                for i in n['participantes']:
                    texto += i + ', '
                texto = texto[:-2]
                texto += '\n\n'
            bot.send_message(message.chat.id, '<b>Lista de gastos:</b>\n\n' + texto, parse_mode="html")
        else:
            bot.send_message(message.chat.id, '<b>No hay ningún gasto en el evento!</b>', parse_mode="html")
        showButtons(bot, message.chat.id)

    @bot.message_handler(commands='BORRARgasto')
    def cmd_borrarGasto(message):
        lista = listar_eventos(message.chat.id)
        if len(lista):
            eventos = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(lista)
            eventos = agrupar_botones(long_list, lista, eventos)
            msg = bot.send_message(message.chat.id, 'Selecciona evento para borrar un gasto:', reply_markup=eventos)
            bot.register_next_step_handler(msg, borrarGastoEvento)
        else:
            bot.send_message(message.chat.id, '<b>No hay eventos.\nCrea primero un evento.</b>', parse_mode="html")
            showButtons(bot, message.chat.id)
    
    def borrarGastoEvento(message):
        dicc_temp['dicc_evento'][message.chat.id] = message.text #Hay que añadir esta línea para que en la ruta del archivo se sepa el evento.
        path = filenameToPath(message)
        dicc_temp['dicc_path'][message.chat.id] = path
        loadData(message.chat.id, path)
        listado = dicc_data[message.chat.id]['gastos']
        if len(listado):
            texto = ''
            for n in listado:
                texto += 'Evento nº' + str(listado.index(n)+1) + ':\n'
                texto += 'Pagador: ' + n['pagador'] + '\n'
                texto += 'Concepto: ' + n['concepto'] + '\n'
                texto += 'Cantidad: ' + str(n['cantidad']) + '\n'
                texto += 'Participantes: '
                for i in n['participantes']:
                    texto += i + ', '
                texto = texto[:-2]
                texto += '\n\n'
            gastos = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(listado)
            lista_numeros = createList(long_list) #Esta lista está pasa de int -> str.
            gastos = agrupar_botones(long_list, lista_numeros, gastos)
            msg = bot.send_message(message.chat.id, 'Selecciona el número del gasto a borrar:\n\n' + texto, reply_markup=gastos)
            bot.register_next_step_handler(msg, dialogBorrarGasto)
        else:
            bot.send_message(message.chat.id, '<b>No hay ningún gasto en el evento!</b>', parse_mode="html")
            showButtons(bot, message.chat.id)

    def dialogBorrarGasto(message):
        dicc_temp['num_gasto_borrar'][message.chat.id] = message.text
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('CONFIRMAR')
        markup.row('CANCELAR')
        msg = bot.send_message(message.chat.id, 'Confirma para borrar gasto <b>nº ' + message.text + '</b>', parse_mode="html", reply_markup=markup)
        bot.register_next_step_handler(msg, borradoFinalGasto)

    def borradoFinalGasto(message):
        if message.text == 'CONFIRMAR':
            dicc_data[message.chat.id]['gastos'].pop(int(dicc_temp['num_gasto_borrar'][message.chat.id])-1)
            bot.send_message(message.chat.id, 'Gasto <b>nº' + dicc_temp['num_gasto_borrar'][message.chat.id] + '</b> borrado!', parse_mode="html")            
            saveData(message.chat.id, dicc_temp['dicc_path'][message.chat.id]) #Lo guardo en el archivo
        showButtons(bot, message.chat.id) #Los botones se van a mostrar luego sea la opción que sea


    @bot.message_handler(commands=['💶CALCULAR💶'])
    def cmd_calcular(message):
        lista = listar_eventos(message.chat.id)
        if len(lista):
            eventos = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(lista)
            eventos = agrupar_botones(long_list, lista, eventos)
            msg = bot.send_message(message.chat.id, 'Selecciona el evento a calcular:', reply_markup=eventos)
            bot.register_next_step_handler(msg, dialogCalcular)
        else:
            msg = bot.send_message(message.chat.id, '<b>No hay eventos para calcular.\nCrea primero un evento.</b>', parse_mode="html")
            showButtons(bot, message.chat.id)

    def dialogCalcular(message):
        dicc_temp['dicc_evento'][message.chat.id] = message.text
        path = filenameToPath(message)
        dicc_temp['dicc_path'][message.chat.id] = path
        loadData(message.chat.id, path)
        listado = dicc_data[message.chat.id]['gastos']
        if len(listado):
            botones = ReplyKeyboardMarkup(resize_keyboard=True)
            botones.row('CALCULAR')
            botones.row('CANCELAR')
            msg = bot.send_message(message.chat.id, 'Confirma el cálculo de la cuenta y mostraré los distintos pagos a realizar.', reply_markup=botones)
            bot.register_next_step_handler(msg, calcular)
        else:      
            bot.send_message(message.chat.id, '<b>No hay ningún gasto en el evento!</b>', parse_mode="html")
            showButtons(bot, message.chat.id)

    def calcular(message):
        loadData(message.chat.id, dicc_temp['dicc_path'][message.chat.id])
        #listado_amigos = list(dicc_data[message.chat.id]['amigos'])
        #listado_gastos = list(dicc_data[message.chat.id]['gastos']) #listado de gastos

        dicc_temp['calculo'][message.chat.id] = {}
        for amigo in dicc_data[message.chat.id]['amigos']:
            dicc_temp['calculo'][message.chat.id][amigo] = {}
            dicc_temp['calculo'][message.chat.id][amigo]['pagado'] = 0  #Iniciamos a cero las cuentas
            dicc_temp['calculo'][message.chat.id][amigo]['debido'] = 0
            dicc_temp['calculo'][message.chat.id][amigo]['diff'] = 0

        #Calculo lo debido y lo pagado
        for gasto in dicc_data[message.chat.id]['gastos']:
            dicc_temp['calculo'][message.chat.id][gasto['pagador']]['pagado'] += int(gasto['cantidad']) #Actualizo todo lo pagado
            for participante in gasto['participantes']:
                dicc_temp['calculo'][message.chat.id][participante]['debido'] += round(float(gasto['cantidad'])/(len(gasto['participantes'])),2) #Actualizo todo lo debido

        dicc_temp['listas'][message.chat.id] = [[[], []], [[], []], ''] #Inicializamos listas    
        #0 RECIBIR, 1 PAGAR, 2 ÍNDICE Y TEXTO SEGUNDA LISTA (EL DE LA PRIMERA LO VOY SACANDO DEL FOR)

        #Calculo las diferencias
        for amigo in dicc_temp['calculo'][message.chat.id]: #Esto es un dicc y no una lista como los gastos.
            dicc_temp['calculo'][message.chat.id][amigo]['diff'] = dicc_temp['calculo'][message.chat.id][amigo]['debido']-dicc_temp['calculo'][message.chat.id][amigo]['pagado']
            if dicc_temp['calculo'][message.chat.id][amigo]['diff'] < 0: #RECIBIR diff negativas
                dicc_temp['listas'][message.chat.id][0][0].append(dicc_temp['calculo'][message.chat.id][amigo]['diff'])
                dicc_temp['listas'][message.chat.id][0][1].append(amigo)
            else: #PAGAR diff positivas
                dicc_temp['listas'][message.chat.id][1][0].append(dicc_temp['calculo'][message.chat.id][amigo]['diff'])
                dicc_temp['listas'][message.chat.id][1][1].append(amigo)

        #indice = dicc_temp['listas'][message.chat.id][2][0]
        j = 0
        for i in range(len(dicc_temp['listas'][message.chat.id][0][0])):
            while abs(dicc_temp['listas'][message.chat.id][0][0][i]) >= dicc_temp['listas'][message.chat.id][1][0][j]: #Mientras el dinero del pagador sea menor que el del que recibe.
                dicc_temp['listas'][message.chat.id][2] += \
                    dicc_temp['listas'][message.chat.id][1][1][j] + \
                    ' debe ' + str(round(dicc_temp['listas'][message.chat.id][1][0][j]),2) + \
                    '€ a ' + dicc_temp['listas'][message.chat.id][0][1][i] + '\n'
                dicc_temp['listas'][message.chat.id][0][0][i] += dicc_temp['listas'][message.chat.id][1][0][j] # Actualizo el dinero del que recibe.

                if (j <= len(dicc_temp['listas'][message.chat.id][0][0])):
                    j += 1 #Subo indice de los pagadores

            if abs(dicc_temp['listas'][message.chat.id][0][0][i]) < dicc_temp['listas'][message.chat.id][1][0][j] and j<len(dicc_temp['listas'][message.chat.id][0][0]):
                dicc_temp['listas'][message.chat.id][1][0][j] += dicc_temp['listas'][message.chat.id][0][0][i]

                dicc_temp['listas'][message.chat.id][2] += \
                    dicc_temp['listas'][message.chat.id][1][1][j] + \
                    ' debe ' + str(round(dicc_temp['listas'][message.chat.id][1][0][j]), 2) + \
                    '€ a ' + dicc_temp['listas'][message.chat.id][0][1][i] + '\n'

        bot.send_message(message.chat.id, '<b>Lista de pagos:</b>\n\n' + dicc_temp['listas'][message.chat.id][2], parse_mode="html")
        showButtons(bot, message.chat.id)

    @bot.message_handler(commands=['▪️OCULTAR_BOTONES▪️'])
    def cmd_hideButtons(message):
        botones = ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Botones ocultos.\nUsa el botón menú o el comando /inicio para volver a mostrarlos.', reply_markup=botones)
#--------------------------------------------------------------------------------------------------
bot_polling()