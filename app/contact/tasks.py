"""
    Celery tasks. Some of them will be launched periodically from admin panel via django-celery-beat
"""
import pandas as pd
import re
import os
import io
from status_db.celery import app
from celery.utils.log import get_task_logger
from django.apps import apps
from django.db.models import Count, CharField, Value
from django.db.models.functions import Concat


logger = get_task_logger(__name__)


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


@app.task(ignore_result=True)
def drop_duplecates(instance_str):
    Model = apps.get_model(app_label='contact', model_name=instance_str)
    dublecates = (
        Model.objects.exclude(tel = '', email = '')
        .filter(tel__isnull = False, email__isnull = False)
        .values('tel', 'email')
        .annotate(comp_string = Count(Concat('tel', Value(' '), 'email', output_field=CharField())) )
        .filter(comp_string__gt=1)
    )
    dublecates.delete()
    

@app.task(ignore_result=True)
def load_data_task(instance_str, file_path, fields, **kwargs):
    logger.info(f"- - - - START loading - - - -")
    print(instance_str, file_path,)
    xlsx = pd.ExcelFile(file_path)
    sheet_names =  [e for e in xlsx.sheet_names if e  != 'hiddenSheet']
    print(sheet_names)
    for sheet_name in sheet_names:
        df = pd.read_excel(xlsx, sheet_name)
        df.columns = list(map(lambda x: x.strip(), df.columns))
        print(' - - - - - - - - - - - - - ', df.columns)
        # parse data
        res = df.apply(
            lambda el: parse_info(el, kwargs[fields[-3][1]], kwargs[fields[-2][1]], kwargs[fields[-1][1]]),
            axis=1, result_type='expand'
        )
        # load data
        for k, v, name in fields[:-3]:
            res[name] = df[kwargs[v]] if kwargs[k] else kwargs.get(v)
        res['whatsapp'] = kwargs.get('whatsapp')
        res['telegram'] = pd.notna(res['tg_username'])
        # save data
        instance = apps.get_model(app_label='contact', model_name=instance_str)
        for _, row in res.iterrows():
            instance.objects.create(**row.to_dict()).save()

    drop_duplecates.delay(instance_str=instance_str)
    
    os.remove(file_path)
    logger.info(f"- - - - FINISH loading - - - -")

@app.task(ignore_result=True)
def set_task(task, instance_str, contact_ids):
    instance = apps.get_model(app_label='contact', model_name=instance_str)
    instance.objects.filter(pk__in=contact_ids).update(task=task)

@app.task(ignore_result=True)
def load_tg_wh(instance_str, data_type, file_path):
    xlsx = pd.ExcelFile(file_path)
    sheet_names =  [e for e in xlsx.sheet_names if e != 'hiddenSheet']
    df = pd.read_excel(xlsx, sheet_names[0])
    df.columns = list(map(lambda x: x.strip().lower(), df.columns))

    instance = apps.get_model(app_label='contact', model_name=instance_str)

    if data_type == 'WhatsApp':
        instance.objects.filter(tel__in=df['phone_number'].to_list()).update(whatsapp=True)
    else:
        for row in df.iterrows():
            instance.objects.filter(tel=row['phone_number']).update(
                telegram=True,
                tg_username=row['username']
            )
    
    



    
