# -*- coding: utf-8 -*-
"""
Created on Wed May 16 10:26:41 2018

@author: Andres
"""
import re
texto_mail=""

import imaplib
import email
pattern="(^.+dias )(?P<dia_desde>.{10})( y )(?P<dia_hasta>.{10})(.*?las )(?P<hora_desde>.{5})(.*?las )(?P<Hora_hasta>.{5})(.*?calle )(?P<calle>.*?)(\(.*?Número )(?P<numero>.*?)( se .*?corte )(?P<tipo_corte>.*?$)"

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('unicangist@gmail.com', 'notienestelefono902')
mail.list()
# Out: list of "folders" aka labels in gmail.
mail.select("INBOX") # connect to inbox.

result, data = mail.search(None, "ALL")

#ids = data[0] # data is a list.
#id_list = ids.split() # ids is a space separated string
#latest_email_id = id_list[-1] # get the latest
v1=''
result, data = mail.search(None, '(FROM "andres.rodriguez@unican.es")')
lista=list()
for num in data[0].split():
    typ, correo = mail.fetch(num, '(RFC822)')

    raw_email=correo[0][1]
    #continue inside the same for loop as above
    raw_email_string = raw_email.decode('iso-8859-1')
    # converts byte literal to string removing b''
    msg = email.message_from_string(raw_email_string)
    msg.get_payload()[0].as_string()
    prog = re.compile(pattern, flags=re.I)
    resultado = prog.match(msg.get_payload()[0].as_string())
    lista.append(msg.get_payload()[0].as_string())
    lista.append(resultado)
    


        
