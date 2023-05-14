# Asistente Kevin
import sys
import re
#import telegram
import asyncio

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler

)

import logging
import pandas as pd
import random

from cfg.tg_token import lverbobot_token

# ----------------------------------------------------------------------------------------
# Logs de usuario
def registra(update: Update, cmd):

    usuario = update.message.from_user

    if (usuario.username is None):
        usuario.username = 'PRIVADO'
    if (usuario.id is None):
            usuario.id = -1
    if (usuario.full_name is None):
        usuario.full_name = 'PRIVADO'
    logging.info(' - CMD: '+ cmd + ' - USER_ID: ' + str(usuario.id) + ' - USERNAME: ' + usuario.username + ' - USER_FULLNAME: ' + usuario.full_name + ' - CHAT ID: ' + str(update.effective_chat.id) )


# ----------------------------------------------------------------------------------------
# Logs de usuario
def registra_boton(update: Update, cmd):

    logging.info(' - CMD: '+ cmd + ' - USER_ID: --' ' - USERNAME: --' + ' - USER_FULLNAME: --' + ' - CHAT ID: ' + str(update.effective_chat.id) )




# ----------------------------------------------------------------------------------------
# Busca palabra clave en cualquier de las columnnas
def busca_clave(df: pd, clave: str):
    mask = df[df.apply(lambda row: row.astype(str).str.contains(clave, case=False).any(), axis=1)]
    #res=df.loc[mask]
    return(mask)


def print_lineas(resultado):
    resultado['texto'] = '*' + resultado['TipoLinea']+'* : ' + resultado['TECNOLOXIA'] + ' '+ resultado['VBO'] + '/'+ resultado['VSO']
    t = resultado['texto'].to_string(index=False)
    return(t)


#HANDLERS






# Definicion de botonera para respuesta
#def botonera():

    #botones = ['Presente de Indicativo','Pretérito imperfecto de Indicativo','Pretérito perfecto de Indicativo','Pretérito pluscuamperfecto de Indicativo','Futuro de Indicativo','Condicional de Indicativo','Presente de Subxuntivo','Pretérito de Subxuntivo','Futuro de Subxuntivo','Infinitivo','Xerundio','Participio','Imperativo']
    #botonera = InlineKeyboardMarkup(botones)
    #return(botonera)




#----------------------------------------------------------------------------------------
# Crea boton
def crea_boton(verbo):
    texto = verbo['tiempo']
    dato = int(verbo['valor'])
    return([InlineKeyboardButton(texto, callback_data=dato)])

# ----------------------------------------------------------------------------------------
# Crea botonnera
def crea_botonera():

    s_botonera = d_tiempos.apply(lambda row: crea_boton(row), axis=1)

    #listado['boton'] = d_verbos.apply(lambda row: boton(row), axis=1)
    #botones = s_botonera.tolist()
    botones = s_botonera.tolist()
    botonera = InlineKeyboardMarkup(botones)
    return(botonera)


# --------------------------------------------------------------------------------------
# Boton pulsado
def boton_pulsado(update: Update, context: CallbackContext):
    query = update.callback_query

    # Las Callbackquerys necesitan ser respondidas. No se exactamente lo que quiere decir eso pero es así. Si n lo haces le sale un relojito al botón
    query.answer()

    respuesta = int(query.data)
    if (respuesta == context.user_data['respuestacorrecta_valor']):
        context.user_data['puntuacion'] = context.user_data['puntuacion'] + context.user_data['respuestacorrecta_valor']
        resultado = 'Has respondido con sabiduría pero era facilona' + '\U0001F973'
        context.bot.send_message(chat_id=update.effective_chat.id, text=resultado)
        registra_boton(update, 'ACIERTO')
    else:
        context.user_data['puntuacion'] = context.user_data['puntuacion'] -10
        resultado = 'Vaya pedazo de error ' + '\U0001F624'
        context.bot.send_message(chat_id=update.effective_chat.id, text=resultado)
        context.bot.send_message(chat_id=update.effective_chat.id, text=context.user_data['respuestacorrecta_texto'],
                             reply_markup=botonera)
        registra_boton(update, 'FALLO')





# --------------------------------------------------------------------------------------
# Comando ditiempo
def ditiempo(update: Update, context: CallbackContext):
    registra(update, 'DITIEMPO')
    pregunta_entrada= selverbo(context)
    context.bot.send_message(chat_id=update.effective_chat.id,text=context.user_data['respuestacorrecta_texto'] ,reply_markup=botonera)


#--------------------------------------------------------------------------------------
# Respuesta
def respuesta(update: Update, context: CallbackContext):
    registra(update, 'RESPUESTA')
    #context.bot.send_message(chat_id=update.effective_chat.id,text='Verboalchou', reply_markup=botonera)
    respuesta = update.message.text.lower()

    if (respuesta == context.user_data['respuestacorrecta_texto']):
        resultado = 'Has respondido con sabiduría ' + '\U0001F973'
        context.user_data['puntuacion'] = context.user_data['puntuacion'] + context.user_data['respuestacorrecta_valor']
        registra(update, 'ACIERTO')
    else:
        resultado = 'Vamos mal, sigue intentándolo ' + '\U0001F624'
        context.user_data  ['puntuacion'] = context.user_data['puntuacion'] - 10
        registra(update,'FALLO')

    context.bot.send_message(chat_id=update.effective_chat.id,text=resultado)


# ----------------------------------------------------------------------------------------
# Selecciona verbo
def pidopapas(update: Update, context: CallbackContext):
    registra(update, 'PIDOPAPAS')
    texto = context.user_data['respuestacorrecta_texto'] +'-' + context.user_data['respuestacorrecta_tiempo'] + 'de ' + context.user_data['respuestacorrecta_modo']
    context.user_data['puntuacion'] = context.user_data['puntuacion'] - 100
    context.bot.send_message(chat_id=update.effective_chat.id, text=texto)
    return()

# ----------------------------------------------------------------


# ----------------------------------------------------------------------------------------
# Selecciona verbo
def selverbo(context: CallbackContext):
    aleatorio = random.randint(1, d_verbos.shape[0])
    pregunta_entrada = d_verbos.iloc[aleatorio]

    context.user_data['respuestacorrecta_texto'] = pregunta_entrada['respuesta']
    context.user_data['respuestacorrecta_valor'] = pregunta_entrada['valor']
    context.user_data['respuestacorrecta_tiempo'] = pregunta_entrada['tiempo']
    context.user_data['respuestacorrecta_modo'] = pregunta_entrada['modo']
    context.user_data['verbo'] = pregunta_entrada['verbo']

    return(pregunta_entrada)

# ----------------------------------------------------------------------------------------
# Comando diverbo
def diverbo(update: Update, context: CallbackContext):
    registra(update,'DIVERBO')

    aleatorio = random.randint(1,d_verbos.shape[0])
    pregunta_entrada = selverbo(context)

    persona = pregunta_entrada['persona'] + ' persona del ' + pregunta_entrada['cuantos']
    modo = pregunta_entrada['modo']
    tiempo = pregunta_entrada['tiempo']
    verbo = pregunta_entrada['verbo'].upper()
    pregunta =  persona + ' del ' + tiempo + ' de ' + modo + ' del verbo ' + verbo

    context.bot.send_message(chat_id=update.effective_chat.id, text=pregunta,)


# ----------------------------------------------------------------------------------------
# Comando puntuacion
def reiniciapuntuacion(update: Update, context: CallbackContext):
    context.user_data['puntuacion'] = 0
    context.bot.send_message(chat_id=update.effective_chat.id,text='Puntuación reiniciada')



# ----------------------------------------------------------------------------------------
# Comando puntuacion
def puntuacion(update: Update, context: CallbackContext):
    puntuacion = context.user_data['puntuacion']
    context.bot.send_message(chat_id=update.effective_chat.id,text='Tu puntuación es de '+ str(puntuacion) + ' puntos')


# ----------------------------------------------------------------------------------------
# Comando start
def start(update: Update, context: CallbackContext):

    context.bot.send_message(chat_id=update.effective_chat.id, text='Hola '+ update.message.chat.first_name)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Bienvenido a tu Bot prepara verbos para Cruz - Especial Salvador de Madariaga.\n')
    registra(update,'START')



def main():
    # Para acceder desde los handlers es más sencillo declarar la variable a nivel global
    global d_verbos
    global d_tiempos
    global botonera


    d_verbos = pd.read_csv(open('input/lverbos.csv'),sep=',')
    d_tiempos = pd.read_csv(open('input/ltiempos.csv'),sep=',')

    botonera = crea_botonera()

    # Permite revisar funcionamiento

    logging.basicConfig(filename='log/lverbobot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # Configuración de los handlers
    updater = Updater(token=lverbobot_token, use_context=True)


    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('diverbo', diverbo))
    dispatcher.add_handler(CommandHandler('ditiempo', ditiempo))
    dispatcher.add_handler(CommandHandler('pidopapas', pidopapas))
    dispatcher.add_handler(CommandHandler('puntuacion', puntuacion))
    dispatcher.add_handler(CommandHandler('reiniciapuntuacion', reiniciapuntuacion))
    dispatcher.add_handler(MessageHandler(Filters.text, respuesta))
    dispatcher.add_handler(CallbackQueryHandler(boton_pulsado))


    updater.start_polling()

    sys.exit()


if __name__ == '__main__':
    main()