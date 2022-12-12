from contact.models import *
from datetime import datetime
import pandas as pd
import re
import os
import io
import csv


MAIL = "[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}"
PHONE = "((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))"

def _parse_phone(x):
    if x is not None:
        x1 = str(x)
        x1 = re.sub('(\()|(\))|(\s+)', '', x1)
        if len(x1) == len('9978255'):
            return '8495' + x1
        elif x1[0] == '8' and not x[:4] == '8495':
            return '+7' + x1[1:]
        elif x1[0] == '7':
            return '+' + x1
    return x

def parse_info(el, phone_name_filed, email_name_filed, fio_name_filed):
    raw_phones = re.sub('\(|\)|-| |\+', '', str(el[phone_name_filed]))
    phones = list(
        map(
            lambda phone: _parse_phone(phone), 
            re.findall(PHONE, raw_phones)
        )
    )
    mails = re.findall(MAIL, str(el[email_name_filed]))
    fio = re.sub('\(|\)|-|\+|[a-z0-9]|\\n', '', str(el[fio_name_filed]))
    phones = phones + [None]*(3-len(phones))
    mails = mails + [None]*(3-len(mails))  
    data = pd.Series({'fio': fio, 'tel': phones[0], 'tel2': phones[1], 'email': mails[0],'email2': mails[1]})
    return data


def load_data(instance, file_path, extra_fields=[], **kwargs):
    # define fields
    fields = extra_fields + [
        ('tg_username_from_table', 'tg_username_filed', 'tg_username'),
        ('country_from_table', 'country_name_field', 'country'),
        ('city_from_table', 'city_name_field', 'city'),
        ('adres_from_table', 'adres_name_field', 'addres'),
        ('phone_name_filed', 'phone_name_filed', ''),
        ('email_name_filed', 'email_name_filed', ''),
        ('fio_name_filed', 'fio_name_filed', ''),
    ]
    if (kwargs['tg_username_from_table'] and len(kwargs['tg_username_filed']) < 3) or (not kwargs['tg_username_from_table']):
        kwargs.pop('tg_username_filed')

    xlsx = pd.ExcelFile(file_path)
    sheet_names = xlsx.sheet_names
    for sheet_name in sheet_names:
        df = pd.read_excel(xlsx, sheet_name)
        # check fields
        columns = list(df.columns)
        for k, v, _ in fields:
            if kwargs[k] and kwargs[v] not in columns:
                raise Exception(kwargs[v], sheet_name)
        # parse data
        res = df.apply(
            lambda el: parse_info(el, kwargs[fields[-3][1]], kwargs[fields[-2][1]], kwargs[fields[-1][1]]),
            axis=1, result_type='expand'
        )
        # load data
        for k, v, name in fields[:-2]:
            res[name] = df[kwargs[v]] if kwargs[k] else kwargs.get(v)
        res['whatsapp'] = kwargs.pop('whatsapp')
        res['telegram'] = res['tg_username'].isnull()
        # save data
        for _, row in res.iterrows():
            instance.objects.create(**row.to_dict()).save()
       





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