from contact.models import *
from datetime import datetime
import pandas as pd
import re
import os
import io
import csv
from contact.tasks import load_data_task



def load_data(instance_str, file_path, extra_fields=[], **kwargs):
    # define fields
    kwargs.pop('file')
    fields = extra_fields + [
        ('tg_username_from_table', 'tg_username_filed', 'tg_username'),
        ('country_from_table', 'country_name_field', 'country'),
        ('city_from_table', 'city_name_field', 'city'),
        ('addres_from_table', 'addres_name_field', 'addres'),
        ('phone_name_filed', 'phone_name_filed', ''),
        ('email_name_filed', 'email_name_filed', ''),
        ('fio_name_filed', 'fio_name_filed', ''),
    ]
    if (kwargs['tg_username_from_table'] and len(kwargs['tg_username_filed']) < 3) \
        or (not kwargs['tg_username_from_table']):
        kwargs.pop('tg_username_filed')

    print('- - - LOAD - - - ', os.path.exists(file_path), file_path)
    xlsx = pd.ExcelFile(file_path)
    sheet_names =  [e for e in xlsx.sheet_names if e != 'hiddenSheet']
    print(sheet_names)
    for sheet_name in sheet_names:
        df = pd.read_excel(xlsx, sheet_name)
        # check fields
        df.columns = list(map(lambda x: x.strip(), df.columns))
        for k, v, _ in fields:
            if kwargs[k] and kwargs[v] not in df.columns:
                raise Exception(f'Поле `{kwargs[v]}` не найдено на листе `{sheet_name}`', df.columns)
    
    load_data_task.delay(
        instance_str=instance_str,
        file_path=file_path,
        fields=fields,
        **kwargs
    )
       





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