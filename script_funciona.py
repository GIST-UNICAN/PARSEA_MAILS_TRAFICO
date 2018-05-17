# -*- coding: utf-8 -*-
"""
Created on Wed May 16 10:26:41 2018

@author: Andres
"""
import re
import contextlib

import imaplib
import email
from mailparser import parse_from_bytes
from contextlib import closing
import googlemaps
from datetime import datetime
import functools
from tools import general
import MySQLdb
import itertools

gmaps = googlemaps.Client(key='AIzaSyCiHoYbihmxJ3U-AA8uPrU-6HET58UiqMc')
pattern = "(^.+dias )(?P<dia_desde>.{10})( y )(?P<dia_hasta>.{10})(.*?las )(?P<hora_desde>.{5})(.*?las )(?P<hora_hasta>.{5})(.*?calle )(?P<calle>.*?)(\(.*?Número )(?P<numero>.*?)( se .*?corte )(?P<tipo_corte>.*?$)"
pattern_numero = "(?P<primer_numero>^[0-9]*)(?P<letras>[ A-Z\-a-z\/ \\ ]*)(?P<segundo_numero>[0-9]*)"
comparador = re.compile(pattern, flags=re.I)
comparador_numero = re.compile(pattern_numero, flags=re.I)
lista = []
lista_bruta = []


def parsea_numero(numero):
    devolver = ""
    try:
        n1 = numero['primer_numero']
        devolver += str(n1)
    except KeyError:
        n1 = None
        pass
    try:
        n2 = numero['segundo_numero']
        devolver += ' - '+str(n2)
    except KeyError:
        n2 = None
        pass
    try:
        media = int((int(n1)+int(n2))/2)
    except TypeError:
        media = None

    return (devolver, (int(n1), int(n2), media))


def aplica_geocode(numero, calle):
    print(numero, calle)
    texto_geocode = f'{calle} {numero} Santander España' if numero else f'{calle} Santander España'
    try:
        d = gmaps.geocode(texto_geocode)[0]['geometry']['location']
        return (d['lat'], d['lng'])
    except:
        print('error')
        return None


lista_query_append = list()
with closing(imaplib.IMAP4_SSL('imap.gmail.com')) as mail:
    mail.login('unicangist@gmail.com', 'notienestelefono902')
    mail.select("INBOX")  # connect to inbox.
    result, data = mail.search(None, '(FROM "andres.rodriguez@unican.es")')
#    for num in data[0].split():

    for num in ("309",):
        try:
            correo_data = mail.fetch(num, '(RFC822)')
        except TypeError:
            continue
        raw_email = correo_data[1][0][1]
        emilio = parse_from_bytes(raw_email)
        texto = emilio.text_plain[0]
        regex_correo = comparador.search(texto)
        try:
            resultado = regex_correo.groupdict()
            lista.append(resultado)
            calle = resultado['calle']
            numero = resultado['numero']
            regex_numero = comparador_numero.search(numero)
            resultado_numero = regex_numero.groupdict()
            numero_formateado = parsea_numero(resultado_numero)
            numero = numero_formateado[0]
            # Geocoding an address
            # la lista contendra hasta 3 tuplas (lat lng) del inicio fin y media de los datos del corte
            geocode_data = list(iter(map(functools.partial(aplica_geocode,
                                                           calle=calle),
                                         numero_formateado[1])))

            # sacamos los datos que faltan
            dia_desde = resultado['dia_desde']
            dia_hasta = resultado['dia_hasta']
            hora_desde = resultado['hora_desde']
            hora_hasta = resultado['hora_hasta']
            desde, hasta = map(datetime.strptime,
                               (dia_desde+' '+hora_desde,
                                dia_hasta+' '+hora_hasta),
                               itertools.repeat('%d/%m/%Y %H:%M', 2))
            desde, hasta = map(str, (desde, hasta))
                        
            primer_numero = numero_formateado[1][0]
            segundo_numero = numero_formateado[1][1]
            lat_desde = geocode_data[0][0]
            long_desde = geocode_data[0][1]
            lat_hasta = geocode_data[1][0]
            long_hasta = geocode_data[1][1]
            tipo_corte = resultado['tipo_corte']
            idcorte=dia_desde+dia_hasta+str(calle)+str(primer_numero)+tipo_corte
            lista_query_append.append((idcorte,desde, hasta, calle, primer_numero,
                                       segundo_numero, lat_desde, long_desde,
                                       lat_hasta, long_hasta, tipo_corte))

        except AttributeError:
            print("{} no es un correo de tráfico.".format(emilio.subject))
            lista_bruta.append(texto)

# con todos los datos descargados se procede a subirlos a la base de datos

querie = "INSERT IGNORE INTO `Incidencias_Trafico` (`id_unico`,`Fecha_desde`, `Fecha_hasta`, `Calle`, `Numero_desde`, `Numero_hasta`, `Lat_desde`, `Long_desde`, `Lat_hasta`, `Long_hasta`, `Tipo_Corte`) VALUES "
with contextlib.closing(MySQLdb.connect(user='agrega_incidencias_trafico',
                                        password='SYwR6al2eFd2u6ia',
                                        host='193.144.208.142',
                                        port=3306,
                                        database='Trafico_Santander'
                                        )) as conexion:
    with contextlib.closing(conexion.cursor()) as cursor:
        lista_txt= str(tuple(lista_query_append))[1:-2] if len(lista_query_append) ==1 else str(tuple(lista_query_append))[1:-1]
        querie_final = querie+lista_txt
        cursor.execute(querie_final)
        conexion.commit()
