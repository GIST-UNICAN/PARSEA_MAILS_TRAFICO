# -*- coding: utf-8 -*-
"""
Created on Wed May 16 10:26:41 2018

@author: Andres
"""
import re
texto_mail=""

import imaplib
import email
from mailparser import parse_from_bytes
from contextlib import closing
import googlemaps
from datetime import datetime

gmaps = googlemaps.Client(key='AIzaSyCiHoYbihmxJ3U-AA8uPrU-6HET58UiqMc')
pattern="(^.+dias )(?P<dia_desde>.{10})( y )(?P<dia_hasta>.{10})(.*?las )(?P<hora_desde>.{5})(.*?las )(?P<hora_hasta>.{5})(.*?calle )(?P<calle>.*?)(\(.*?Número )(?P<numero>.*?)( se .*?corte )(?P<tipo_corte>.*?$)"
pattern_numero="(?P<primer_numero>^[0-9]*)(?P<letras>[ A-Z\-a-z\/ \\ ]*)(?P<segundo_numero>[0-9]*)"
comparador = re.compile(pattern, flags=re.I)
lista = []
lista_bruta = []
with closing(imaplib.IMAP4_SSL('imap.gmail.com')) as mail:
    mail.login('unicangist@gmail.com', 'notienestelefono902')
    mail.select("INBOX") # connect to inbox.
    result, data = mail.search(None, '(FROM "andres.rodriguez@unican.es")')
#    for num in data[0].split():
    
    for num in ("309",):
        try:
            correo_data = mail.fetch(num, '(RFC822)')
        except TypeError:
            continue
        raw_email=correo_data[1][0][1]
        emilio = parse_from_bytes(raw_email)
        texto = emilio.text_plain[0]
        match = comparador.search(texto)
        try:
            resultado=match.groupdict()
            lista.append(resultado)
            
            calle=resultado['calle']
            numero= resultado ['numero']
            # Geocoding an address
            geocode_result = gmaps.geocode(f'{calle} {numero} Santander España')
        except AttributeError:
            print("{} no es un correo de tráfico.".format(emilio.subject))
            lista_bruta.append(texto)