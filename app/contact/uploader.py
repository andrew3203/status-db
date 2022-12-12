from contact.models import *
from datetime import datetime
import pandas as pd
import re
import os
import io
import csv


MAIL = "[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}"
PHONE = "((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))"


def f(el, phone_name, mail_name, fio_name):
    a = re.sub('\(|\)|-| |\+', '', str(el[phone_name]))
    phones = re.findall(PHONE, a)
    
    mails = re.findall(MAIL, str(el[mail_name]))
    
    fio = re.sub('\(|\)|-|\+|[a-z0-9]|\\n', '', str(el[fio_name]))
    
    phones = phones + [None]*(2-len(phones))
    mails = mails + [None]*(2-len(mails))  
      
    return pd.Series([fio] + mails[:2] + phones[:2])


    
# res = df.apply(f, axis=1, result_type='expand')
# res.head(30)


def _get_csv_from_qs_values(queryset, filename: str = 'contacts'):
    keys = queryset[0].keys()

    # csv module can write data in io.StringIO buffer only
    s = io.StringIO()
    dict_writer = csv.DictWriter(s, fieldnames=keys)
    dict_writer.writeheader()
    dict_writer.writerows(queryset)
    s.seek(0)

    # python-telegram-bot library can send files only from io.BytesIO buffer
    # we need to convert StringIO to BytesIO
    buf = io.BytesIO()

    # extract csv-string, convert it to bytes and write to buffer
    buf.write(s.getvalue().encode(encoding='cp1251'))
    buf.seek(0)

    # set a filename with file's extension
    buf.name = f"{filename}__{datetime.now().strftime('%Y.%m.%d.%H.%M')}.csv"

    return buf, buf.name