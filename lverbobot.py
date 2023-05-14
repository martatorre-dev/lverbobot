# Asistente Kevin
import sys
#import re
import telegram
#from telegram import (
#    Update,
#    InlineKeyboardMarkup,
#    InlineKeyboardButton,
#    ReplyKeyboardMarkup,
#    KeyboardButton,
#)

from telegram.ext import (
    Updater,
    CommandHandler,
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
    usuario=update.message.from_user
    if (usuario.username is None):
        usuario.username = 'PRIVADO'
    if (usuario.id is None):
            usuario.id = -1
    if (usuario.full_name is None):
        usuario.full_name = 'PRIVADO'
    logging.info(' - CMD: '+ cmd + ' - USER_ID: ' + str(usuario.id) + ' - USERNAME: ' + usuario.username + ' - USER_FULLNAME: ' + usuario.full_name + ' - CHAT ID: ' + str(update.effective_chat.id) )




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
#----------------------------------------------------------------------------------------
# Comando lineas
# lineas - Muestra las líneas de una sede
def lineas(update: Update, context: CallbackContext):


    if not(revision_comando(update, context)):
        return 0

    codigo=context.user_data['sf']

    texto = 'Estas son las líneas asociadas a la sede *' + codigo + '*\n'
    # TODO : arreglar el formato
    resultado = d_lineas.loc[d_lineas['SF'] == codigo][['TipoLinea', 'TECNOLOXIA', 'VBO', 'VSO']]
    #t_resultado = resultado.to_string(index=False)
    t_resultado = print_lineas(resultado)
    texto = texto + '\n' + t_resultado


    #update.message.reply_text(text=texto, parse_mode = 'Markdown')
    context.bot.send_message(chat_id=update.effective_chat.id, text=texto, parse_mode = 'Markdown')
    registra(update, 'LINEAS')

# ---------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# Comando busca
# Busca el código de una sede basado en palabras introducidas por el usuario
#NTG
#PD
def busca(update: Update, context: CallbackContext):
    if (not (usuario_autorizado(update))):
        return 0

    listado = busca_sedes(context.args)
    if (len(listado)>0):
        listado['boton'] = listado.apply(lambda row: boton(row), axis=1)
        botones = listado['boton'].tolist()
        botonera = InlineKeyboardMarkup(botones)

        context.bot.send_message(chat_id=update.effective_chat.id,text='Estas son las dependencias que coinciden con tu búsqueda:', reply_markup=botonera)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Sin resultados')
    registra(update, 'BUSCA')



#----------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------
# Print dependencia con formato
def print_sede(update: Update, context: CallbackContext,codigo):
    dep = dependencias.loc[dependencias['SF'] == codigo][['SF', 'LATITUDE', 'LONXITUDE', 'PROVINCIA', 'CONCELLO', 'C_POSTAL', 'POBOACION', 'NUCLEO', 'ENDEREZO']]
    org = sedes.loc[sedes['SF'] == codigo][['DEPENDENCIA']]
    texto = '* ' + dep['SF'].values[0] + ' - ' + org['DEPENDENCIA'].values[0] + '* \n'
    dd=dep.to_dict(orient='records')[0]


    for clave,valor in dd.items():
        try:
            if (valor == 'NA'):
                dd[clave]=''
            if ((clave == 'LATITUDE') | (clave == 'LONXITUDE')):
                dd[clave] = dd[clave].replace(',','.')
        except Exception as e:
            print(e)


    texto = texto + dd['PROVINCIA'] + ' ' + dd['C_POSTAL'] + '\n'
    texto = texto + dd['CONCELLO'] +  ' ' + dd['POBOACION'] + ' ' + dd['NUCLEO'] + '\n'
    texto = texto + dd['ENDEREZO'] + '\n'
   # texto = texto + 'Coordenadas GPS: ' + dd['LATITUDE'] + ',' + dd['LONXITUDE'] + '\nhttps://google.com/maps?q='+dd['LATITUDE']+','+dd['LONXITUDE']+'\n'
    context.bot.send_message(chat_id=update.effective_chat.id, text=texto, parse_mode='Markdown')
    context.bot.send_location(chat_id=update.effective_chat.id, latitude=float(dd['LATITUDE']), longitude=float(dd['LONXITUDE']))


# ----------------------------------------------------------------------------------------
# Comando seleciona el código de dependencia en uso
# La sede tambien se puede seleccionar como argumento en un comando o tras /busca

def sede(update: Update, context: CallbackContext):
    if (not(usuario_autorizado(update))):
        return 0

    texto=''
    if (len(context.args) > 0):
        codigo = context.args[0]
        if (formato_sf(codigo)):
            context.user_data['sf'] = codigo
        else:
            texto = 'Código de dependencia incorrecto'

    if (context.user_data['sf'] != ''):
        texto = ' Usando *' + context.user_data['sf'] + '* como código de dependencia\n'
        context.bot.send_message(chat_id=update.effective_chat.id, text=texto, parse_mode='Markdown')
        resultado = dependencias.loc[dependencias['SF'] == context.user_data['sf']][['SF', 'LATITUDE', 'LONXITUDE', 'PROVINCIA','CONCELLO','C_POSTAL','POBOACION','NUCLEO','ENDEREZO']]
        t_resultado = resultado.to_dict(orient='records')[0]
        #texto = 'Coordenadas GPS:' resultado['LATITUDE']
        #(t,lt,lg) =  print_sede(context.user_data['sf'])
        #texto=texto + t



    #context.bot.send_location(chat_id=update.effective_chat.id,latitude=lt,longitude=lg)
    registra(update,'SEDE')



# Definicion de botonera para respuesta
def botonera():

    botones = ['Presente de Indicativo','Pretérito imperfecto de Indicativo','Pretérito perfecto de Indicativo','Pretérito pluscuamperfecto de Indicativo','Futuro de Indicativo','Condicional de Indicativo','Presente de Subxuntivo','Pretérito de Subxuntivo','Futuro de Subxuntivo','Infinitivo','Xerundio','Participio','Imperativo']
    botonera = InlineKeyboardMarkup(botones)
    return(botonera)




#----------------------------------------------------------------------------------------
# Crea boton
def boton(verbo):
    texto = verbo['tiempo']
    dato = verbo['valor']
    return([InlineKeyboardButton(texto, callback_data=dato)])




# --------------------------------------------------------------------------------------
# Boton pulsado
def boton_pulsado(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Has seleccionado el Tiempo: {query.data}")
    context.user_data['tiempo']=query.data

    #print_sede(update, context, context.user_data['sf'])

# --------------------------------------------------------------------------------------
# Comando ditiempo
def ditiempo(update: Update, context: CallbackContext):
    registra(update, 'DITIEMPO')

    listado['boton'] = listado.apply(lambda row: boton(verbo), axis=1)
    botones = listado['boton'].tolist()
    botonera = InlineKeyboardMarkup(botones)

    context.bot.send_message(chat_id=update.effective_chat.id,text='Verboalchou', reply_markup=botonera)






# ----------------------------------------------------------------------------------------
# Comando diverbo
def diverbo(update: Update, context: CallbackContext):
    registra(update,'DIVERBO')
    aleatorio = random.randint(1,d_verbos.size)
    pregunta = df.iloc[aleatorio]
    context.bot.send_message(chat_id=update.effective_chat.id, text=pregunta)



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

    d_verbos = pd.read_csv(open('input/lverbos.csv'),sep=',')
    d_tiempos = pd.read_csv(open('input/ltiempos.csv'),sep=',')

    # Permite revisar funcionamiento

    logging.basicConfig(filename='log/lverbobot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # Configuración de los handlers
    updater = Updater(token=lverbobot_token, use_context=True)


    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('diverbo', diverbo))
    dispatcher.add_handler(CommandHandler('ditiempo', ditiempo))
    dispatcher.add_handler(CallbackQueryHandler(boton_pulsado))


    updater.start_polling()

    sys.exit()


if __name__ == '__main__':
    main()