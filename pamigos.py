# -*- coding: utf-8 -*-
import telebot
from time import sleep
from os import remove
from telebot.types import ReplyKeyboardMarkup, ForceReply, ReplyKeyboardRemove
import json, os

with open('config.json', 'r') as file:  config = json.load(file)

BOT_TOKEN = config['TOKEN']['PAmiGOSbot']
DIRECTORIO_RAIZ = config['ROOT_PATH']

WAIT_MENUPPAL = 0.16
WAIT_NAVEGACION = 0.08
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
    sleep(WAIT_MENUPPAL)
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
    mensaje = message.text.replace(' ', '-')
    mensaje = mensaje.replace('_', '-')
    nombre = str(message.chat.id) + '_' + str(mensaje)
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
        sleep(WAIT_NAVEGACION)
        texto = 'Si te ha gustado mi bot y te resulta útil, ayudando con un café contribuirás al mantenimiento y desarrollo de PAmiGOS.\n'
        texto += '<a href= "https://ko-fi.com/theobserver8">https://ko-fi.com/theobserver8</a>'
        bot.send_message(message.chat.id, texto, parse_mode="html")

    @bot.message_handler(commands=['AYUDA❓'])
    def cmd_help(message):
        sleep(WAIT_NAVEGACION)
        botones = ReplyKeyboardRemove()
        texto = '<b>📝 <u>EVENTO</u> 📝</b>: Nombre del evento organizado.\nEjemplo: Madrid.'
        texto += '\n\n<b>🚶🏼‍♂️ <u>AMIGOS</u> 🚶🏻‍♀️</b>: Amigos que forman parte de ese evento. Añade tantos como desees, escribiendo su nombre directamente.'
        texto += '\n\n<b>💰 <u>GASTOS</u> 💰</b>: Distintos gastos del evento.\nEjemplo: Alojamiento, gasolina, entradas, comida...'
        texto += '\n\n<b>💶 <u>CALCULAR</u> 💶</b>: Muestra los pagos a realizar entre vosotros para que las cuentas queden ajustadas.\nTambién es posible mostrar los saldos, que indican lo que cada uno tiene (de forma independiente) que recibir o pagar de forma independiente.'
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
        sleep(WAIT_NAVEGACION)
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Vas a crear un nuevo evento.\nIntroduce el nombre:', reply_markup=markup)
        bot.register_next_step_handler(msg, crear_archivo)

    def crear_archivo(message):
        sleep(WAIT_NAVEGACION)
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
        sleep(WAIT_NAVEGACION)
        listado = listar_eventos(message.chat.id)
        if len(listado):
            listado_lineas = ('\n - '.join(listado)) #Listado separado en líneas
            bot.send_message(message.chat.id, '<b>La lista de eventos es:</b>\n ' + '- ' + listado_lineas, parse_mode="html")
        else:
            bot.send_message(message.chat.id, '<b>La lista de eventos está vacia!</b>', parse_mode="html")
        showButtons(bot, message.chat.id)

    @bot.message_handler(commands=['BORRARevento'])
    def cmd_borrarEvento(message):
        sleep(WAIT_NAVEGACION)
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
        sleep(WAIT_NAVEGACION)
        lista = listar_eventos(message.chat.id)
        if message.text in lista:
            dicc_temp['dicc_evento'][message.chat.id] = message.text
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('CONFIRMAR')
            markup.row('/CANCELAR')
            msg = bot.send_message(message.chat.id, 'Confirma para borrar: <b>' + message.text + '</b>', parse_mode="html", reply_markup=markup)
            bot.register_next_step_handler(msg, borradoFinalEvento)
        else:
            bot.send_message(message.chat.id, 'Introducido nombre de evento incorrecto.\nUtiliza los botones.')
            showButtons(bot, message.chat.id) #Los botones se van a mostrar luego sea la opción que sea
    
    def borradoFinalEvento(message):
        sleep(WAIT_NAVEGACION)
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
        sleep(WAIT_NAVEGACION)
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
        sleep(WAIT_NAVEGACION)
        lista = listar_eventos(message.chat.id)
        if message.text in lista:
            dicc_temp['dicc_evento'][message.chat.id] = message.text
            path = filenameToPath(message)
            loadData(message.chat.id, path)
            dicc_temp['dicc_path'][message.chat.id] = path
            markup = ForceReply()
            msg = bot.send_message(message.chat.id, 'Introduce el nombre de tu amigo:', reply_markup=markup)
            bot.register_next_step_handler(msg, leerAmigo)
        else:
            bot.send_message(message.chat.id, 'Introducido nombre de evento incorrecto.\nUtiliza los botones.')
            showButtons(bot, message.chat.id) #Los botones se van a mostrar luego sea la opción que sea

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
        sleep(WAIT_NAVEGACION)
        if message.text == 'SI':
            markup = ForceReply()
            msg = bot.send_message(message.chat.id, 'Introduce el nombre del amigo:', reply_markup=markup)
            bot.register_next_step_handler(msg, leerAmigo)
        else:
            saveData(message.chat.id, dicc_temp['dicc_path'][message.chat.id]) #Lo guardo en el archivo
            showButtons(bot, message.chat.id)

    @bot.message_handler(commands='VERamigos')
    def cmd_verAmigos(message):
        sleep(WAIT_NAVEGACION)
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
        sleep(WAIT_NAVEGACION)
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
        sleep(WAIT_NAVEGACION)
        lista = listar_eventos(message.chat.id)
        if len(lista):
            eventos = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(lista)
            eventos = agrupar_botones(long_list, lista, eventos)
            msg = bot.send_message(message.chat.id, 'Selecciona evento para borrar amigos:', reply_markup=eventos)
            bot.register_next_step_handler(msg, borrarAmigosEvento)
        else:
            bot.send_message(message.chat.id, '<b>No hay eventos para borrar amigos.\nCrea primero un evento.</b>', parse_mode="html")
            showButtons(bot, message.chat.id)

    def borrarAmigosEvento(message):
        sleep(WAIT_NAVEGACION)
        lista_eventos = listar_eventos(message.chat.id)
        if message.text in lista_eventos:
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
        else:
            bot.send_message(message.chat.id, 'Introducido nombre de evento incorrecto.\nUtiliza los botones.')
            showButtons(bot, message.chat.id) #Los botones se van a mostrar luego sea la opción que sea

    def dialogBorrarAmigo(message):
        sleep(WAIT_NAVEGACION)
        lista_amigos = dicc_data[message.chat.id]['amigos']
        if message.text in lista_amigos:
            dicc_temp['dicc_amigo_temp'][message.chat.id] = message.text
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('CONFIRMAR')
            markup.row('/CANCELAR')
            msg = bot.send_message(message.chat.id, 'Confirma para borrar: <b>' + message.text + '</b>', parse_mode="html", reply_markup=markup)
            bot.register_next_step_handler(msg, borradoFinalAmigo)
        else:
            bot.send_message(message.chat.id, 'Introducido nombre de amigo incorrecto.\nUtiliza los botones.')
            showButtons(bot, message.chat.id) #Los botones se van a mostrar luego sea la opción que sea
    
    def borradoFinalAmigo(message):
        sleep(WAIT_NAVEGACION)
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
        sleep(WAIT_NAVEGACION)
        lista = listar_eventos(message.chat.id)
        if len(lista):
            eventos = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(lista)
            eventos = agrupar_botones(long_list, lista, eventos)
            msg = bot.send_message(message.chat.id, 'Selecciona el evento al que añadir gasto:', reply_markup=eventos)
            bot.register_next_step_handler(msg, nuevoGastoEvento)
        else:
            bot.send_message(message.chat.id, '<b>No hay eventos para añadir gastos.\nCrea primero un evento.</b>', parse_mode="html")
            showButtons(bot, message.chat.id)

    def nuevoGastoEvento(message):
        sleep(WAIT_NAVEGACION)
        lista = listar_eventos(message.chat.id)
        if message.text in lista:
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
                msg = bot.send_message(message.chat.id, '¿Quién ha pagado este gasto?', reply_markup=amigos)
                bot.register_next_step_handler(msg, leerPagadorPedirConcepto)
            else:
                bot.send_message(message.chat.id, '<b>No hay ningún amigo en el evento!</b>', parse_mode="html")
                showButtons(bot, message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Introducido nombre de evento incorrecto.\nUtiliza los botones.')
            showButtons(bot, message.chat.id) #Los botones se van a mostrar luego sea la opción que sea

    def leerPagadorPedirConcepto(message):
        sleep(WAIT_NAVEGACION)
        dicc_temp['dicc_gasto'][message.chat.id]['pagador'] = message.text
        dicc_temp['amigos'][message.chat.id].remove(message.text) #Elimino al pagador del listado de amigos a aparecer
        dicc_temp['dicc_gasto'][message.chat.id]['participantes'] = [message.text] #Añado el pagador a los participantes
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Introduce el concepto del gasto:', reply_markup=markup)
        bot.register_next_step_handler(msg, leerConceptoPedirCantidad)

    def leerConceptoPedirCantidad(message):
        sleep(WAIT_NAVEGACION)
        dicc_temp['dicc_gasto'][message.chat.id]['concepto'] = message.text
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Introduce la cantidad pagada:', reply_markup=markup)
        bot.register_next_step_handler(msg, leerCantidadPedirParticipantes)

    def leerCantidadPedirParticipantes(message):
        sleep(WAIT_NAVEGACION)
        cantidad = message.text.replace(',', '.')
        dicc_temp['dicc_gasto'][message.chat.id]['cantidad'] = cantidad
        if message.text.replace('.', '', 1).isdigit() or message.text.replace(',', '', 1).isdigit():
            dicc_temp['amigos'][message.chat.id].append('FIN 🔚') #Añado un elemento llamado FIN
            participantes = ReplyKeyboardMarkup(resize_keyboard=True)
            long_list = len(dicc_temp['amigos'][message.chat.id])
            participantes = agrupar_botones(long_list, dicc_temp['amigos'][message.chat.id], participantes)
            msg = bot.send_message(message.chat.id, 'Selecciona los amigos que han participado:', reply_markup=participantes)
            bot.register_next_step_handler(msg, pedirParticipantesGuardarGasto)        
        else:
            msg = bot.send_message(message.chat.id, 'ERROR: La cantidad debe de ser un número.\nIntroduce la cantidad pagada:')
            bot.register_next_step_handler(msg, leerCantidadPedirParticipantes) #Volvemos a ejecutar esta función

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
            msg = bot.send_message(message.chat.id, 'Selecciona los amigos que han participado:', reply_markup=participantes_restantes)
            bot.register_next_step_handler(msg, pedirParticipantesGuardarGasto) #Recurro a esta función

    @bot.message_handler(commands='VERgastos')
    def cmd_verGastos(message):
        sleep(WAIT_NAVEGACION)
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
        sleep(WAIT_NAVEGACION)
        lista = listar_eventos(message.chat.id)
        if message.text in lista:
            dicc_temp['dicc_evento'][message.chat.id] = message.text #Hay que añadir esta línea para que en la ruta del archivo se sepa el evento.
            path = filenameToPath(message)
            loadData(message.chat.id, path)
            listado = dicc_data[message.chat.id]['gastos']
            if len(listado):
                texto = ''
                for n in listado:
                    texto += '<u><b>Evento nº' + str(listado.index(n)+1) + ':</b></u>\n'
                    texto += '<b>·Pagador:</b> ' + n['pagador'] + '\n'
                    texto += '<b>·Concepto:</b> ' + n['concepto'] + '\n'
                    texto += '<b>·Cantidad:</b> ' + str(n['cantidad']).replace('.', ',') + '€\n'
                    texto += '<b>·Participantes:</b> '
                    for i in n['participantes']:
                        texto += i + ', '
                    texto = texto[:-2]
                    texto += '\n\n'
                bot.send_message(message.chat.id, '<b>Lista de gastos:</b>\n\n' + texto, parse_mode="html")
            else:
                bot.send_message(message.chat.id, '<b>No hay ningún gasto en el evento!</b>', parse_mode="html")
            showButtons(bot, message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Introducido nombre de evento incorrecto.\nUtiliza los botones.')
            showButtons(bot, message.chat.id) #Los botones se van a mostrar luego sea la opción que sea

    @bot.message_handler(commands='BORRARgasto')
    def cmd_borrarGasto(message):
        sleep(WAIT_NAVEGACION)
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
        sleep(WAIT_NAVEGACION)
        lista = listar_eventos(message.chat.id)
        if message.text in lista:
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
        else:
            bot.send_message(message.chat.id, 'Introducido nombre de evento incorrecto.\nUtiliza los botones.')
            showButtons(bot, message.chat.id) #Los botones se van a mostrar luego sea la opción que sea

    def dialogBorrarGasto(message):
        sleep(WAIT_NAVEGACION)
        listado = dicc_data[message.chat.id]['gastos']
        long_list = len(listado)
        lista_numeros = createList(long_list)
        if message.text in lista_numeros:
            dicc_temp['num_gasto_borrar'][message.chat.id] = message.text
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('CONFIRMAR')
            markup.row('/CANCELAR')
            msg = bot.send_message(message.chat.id, 'Confirma para borrar gasto <b>nº ' + message.text + '</b>', parse_mode="html", reply_markup=markup)
            bot.register_next_step_handler(msg, borradoFinalGasto)
        else:
            bot.send_message(message.chat.id, 'Introducido número de gasto incorrecto.\nUtiliza los botones.')
            showButtons(bot, message.chat.id) #Los botones se van a mostrar luego sea la opción que sea

    def borradoFinalGasto(message):
        sleep(WAIT_NAVEGACION)
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
        sleep(WAIT_NAVEGACION)
        lista = listar_eventos(message.chat.id)
        if message.text in lista:
            dicc_temp['dicc_evento'][message.chat.id] = message.text
            path = filenameToPath(message)
            dicc_temp['dicc_path'][message.chat.id] = path
            loadData(message.chat.id, path)
            listado = dicc_data[message.chat.id]['gastos']
            if len(listado):
                botones = ReplyKeyboardMarkup(resize_keyboard=True)
                botones.row('SALDOS', 'PAGOS')
                botones.row('/CANCELAR')
                msg = bot.send_message(message.chat.id, 'Selecciona si quieres ver los saldos individuales o los pagos entre vosotros para cuadrar las cuentas.', reply_markup=botones)
                bot.register_next_step_handler(msg, calcular)
            else:      
                bot.send_message(message.chat.id, '<b>No hay ningún gasto en el evento!</b>', parse_mode="html")
                showButtons(bot, message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Introducido nombre de evento incorrecto.\nUtiliza los botones.')
            showButtons(bot, message.chat.id) #Los botones se van a mostrar luego sea la opción que sea  

    def calcular(message):
        loadData(message.chat.id, dicc_temp['dicc_path'][message.chat.id])

        dicc_temp['calculo'][message.chat.id] = {}
        for amigo in dicc_data[message.chat.id]['amigos']:
            dicc_temp['calculo'][message.chat.id][amigo] = {}
            dicc_temp['calculo'][message.chat.id][amigo]['pagado'] = 0  #Iniciamos a cero las cuentas
            dicc_temp['calculo'][message.chat.id][amigo]['debido'] = 0
            dicc_temp['calculo'][message.chat.id][amigo]['diff'] = 0
            prueba = 0

        #Calculo lo debido y lo pagado
        for gasto in dicc_data[message.chat.id]['gastos']:
            #Hay que hacer la movida por los decimales. Ej. 23.75 entre 3 da 7.91666 que es 7.92. Vuelvo a multiplicar y redondeo para que cuadre con 23.76
            dicc_temp['calculo'][message.chat.id][gasto['pagador']]['pagado'] += round(round(float(gasto['cantidad'])/(len(gasto['participantes'])), 2) * len(gasto['participantes']), 2) #Actualizo todo lo pagado
            for participante in gasto['participantes']:
                dicc_temp['calculo'][message.chat.id][participante]['debido'] += round(float(gasto['cantidad'])/(len(gasto['participantes'])), 2) #Actualizo todo lo debido

        dicc_temp['listas'][message.chat.id] = [[[], []], [[], []], ''] #Inicializamos listas    
        #0 RECIBIR, 1 PAGAR, 2 TEXTO SEGUNDA LISTA (EL DE LA PRIMERA LO VOY SACANDO DEL FOR)
        #Calculo las diferencias
        for amigo in dicc_temp['calculo'][message.chat.id]: #Esto es un dicc y no una lista como los gastos.
            #TRUNCO a 2 decimales
            if dicc_temp['calculo'][message.chat.id][amigo]['debido']-dicc_temp['calculo'][message.chat.id][amigo]['pagado'] == 0: #Por si alguien está como amigo pero no interviene.
                dicc_temp['calculo'][message.chat.id][amigo]['diff'] = 0
            else:
                dicc_temp['calculo'][message.chat.id][amigo]['diff'] = round((dicc_temp['calculo'][message.chat.id][amigo]['debido']-dicc_temp['calculo'][message.chat.id][amigo]['pagado']), 2)
            
            if dicc_temp['calculo'][message.chat.id][amigo]['diff'] < 0: #RECIBIR diff negativas
                dicc_temp['listas'][message.chat.id][0][0].append(dicc_temp['calculo'][message.chat.id][amigo]['diff'])
                dicc_temp['listas'][message.chat.id][0][1].append(amigo)
            else: #PAGAR diff positivas
                dicc_temp['listas'][message.chat.id][1][0].append(dicc_temp['calculo'][message.chat.id][amigo]['diff'])
                dicc_temp['listas'][message.chat.id][1][1].append(amigo)

        if message.text == 'SALDOS':
            for amigo in dicc_temp['calculo'][message.chat.id]:
                dicc_temp['listas'][message.chat.id][2] += '- ' + amigo + ': ' + str(dicc_temp['calculo'][message.chat.id][amigo]['diff']) + '€\n'
            bot.send_message(message.chat.id, '<b>El saldo de cada amigo es:\n(Negativo) -> </b> le deben dinero.\n<b>(Positivo) -> </b> tiene que pagar.\n' + dicc_temp['listas'][message.chat.id][2], parse_mode="html")
            showButtons(bot, message.chat.id)
        elif message.text == 'PAGOS':
            j = 0
            for i in range(len(dicc_temp['listas'][message.chat.id][0][0])):
                while dicc_temp['listas'][message.chat.id][0][0][i] != 0:
                    if abs(dicc_temp['listas'][message.chat.id][0][0][i]) >= dicc_temp['listas'][message.chat.id][1][0][j]:
                        dicc_temp['listas'][message.chat.id][2] += \
                            dicc_temp['listas'][message.chat.id][1][1][j] + \
                            ' debe ' + str("{0:.2f}".format(dicc_temp['listas'][message.chat.id][1][0][j])) + \
                            '€ a ' + dicc_temp['listas'][message.chat.id][0][1][i] + '\n'
                        dicc_temp['listas'][message.chat.id][0][0][i] += dicc_temp['listas'][message.chat.id][1][0][j] #Actualizo cantidad lista 1
                        dicc_temp['listas'][message.chat.id][0][0][i] = round(dicc_temp['listas'][message.chat.id][0][0][i], 2) #Redondear float anterior a 2 decimales
                        j += 1 #Solo aumento la j en este caso
                    else:
                        dicc_temp['listas'][message.chat.id][1][0][j] += dicc_temp['listas'][message.chat.id][0][0][i] #Actualizo cantidad lista 2
                        dicc_temp['listas'][message.chat.id][1][0][j] = round(dicc_temp['listas'][message.chat.id][1][0][j], 2)
                        dicc_temp['listas'][message.chat.id][2] += \
                            dicc_temp['listas'][message.chat.id][1][1][j] + \
                            ' debe ' + str("{0:.2f}".format(abs(dicc_temp['listas'][message.chat.id][0][0][i]))) + \
                            '€ a ' + dicc_temp['listas'][message.chat.id][0][1][i] + '\n'
                        dicc_temp['listas'][message.chat.id][0][0][i] = 0 #Actualizo cantidad lista 1 para ayudar al while

            bot.send_message(message.chat.id, '<b>Lista de pagos a realizar entre vosotros para cuadrar las cuentas:</b>\n\n' + dicc_temp['listas'][message.chat.id][2], parse_mode="html")
            showButtons(bot, message.chat.id)
        else:
            bot.send_message(message.chat.id, 'Introducida opción incorrecta.\nUtiliza los botones.')
            showButtons(bot, message.chat.id)

    @bot.message_handler(commands=['▪️OCULTAR_BOTONES▪️'])
    def cmd_hideButtons(message):
        botones = ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Botones ocultos.\nUsa el botón menú o el comando /inicio para volver a mostrarlos.', reply_markup=botones)
#--------------------------------------------------------------------------------------------------
bot_polling()