from django import forms
from contact.models import *
from django.core.files.storage import default_storage
from contact.uploader import load_data
from status_db.settings import MEDIA_ROOT
import os

class ContactForm(forms.Form):
    phone_name_filed= forms.CharField(
        label='Поле с телефонами',
        initial='Телефон',
        help_text='Название поля, в котором содержится телефон',
        required=False
    )
    email_name_filed= forms.CharField(
        label='Поле с почтами',
        initial='Почта',
        help_text='Название поля, в котором содержится почта',
        required=False
    )
    fio_name_filed= forms.CharField(
        label='Поле с ФИО',
        initial='ФИО',
        help_text='Название поля, в котором содержится ФИО',
        required=False
    )

    file = forms.FileField(
        label='Данные',
        help_text='В формате xlsx',
        required=True
    )


    tg_username_from_table = forms.BooleanField(
        label = 'Брать telegram username из файла',
        help_text='Если не указано, то telegram username не будет у контактов',
        initial=False, required=False
    )
    tg_username_filed = forms.CharField(
        label = 'Телеграм',
        help_text='Название поля, в котором содержится username Telegram',
        max_length=20,
        initial=None, required=False
    )
    

    whatsapp = forms.BooleanField(
        label = 'Есть в WhatsApp',
        help_text='Все контакты есть в WhatsApp',
        initial=False, required=False
    )

    country_from_table= forms.BooleanField(
        label='Брать название страны из файлы',
        help_text='Если не указано, то страна будет взята из поля ниже',
        initial=False, required=False
    )
    country_name_field= forms.CharField(
        label='Страна',
        help_text='Страна контактов или название поля в файле',
        required=True
    )

    city_from_table= forms.BooleanField(
        label='Брать название горда из файлы',
        help_text='Если не указано, то город будет взят из поля ниже',
        initial=False, required=False
    )
    city_name_field= forms.CharField(
        label='Город',
        help_text='Город контактов или название поля в файле',
        required=True
    )

    addres_from_table= forms.BooleanField(
        label='Брать адрес из файлы',
        help_text='Если не указано, то город будет взят из поля ниже',
        initial=False, required=False
    )
    addres_name_field= forms.CharField(
        label='Адрес',
        help_text='Адрес контактов или название поля в файле',
        required=True
    )
    def save(self):
        file_path = f'{MEDIA_ROOT}/data.xlsx'
        if os.path.exists(file_path):
            os.remove(file_path)
        
        print('PRE SAVE', os.path.exists(file_path), file_path)
        with open(file_path, 'wb+') as destination:
            for chunk in self.cleaned_data['file'].chunks():
                destination.write(chunk)
        print('PRE SAVE', os.path.exists(file_path), file_path)


class RequestContactForm(ContactForm):
    source_from_table = forms.BooleanField(
        label='Брать источник из файлы',
        help_text='Если не указано, то источник будет взят из поля ниже',
        initial=False, required=False
    )
    source_name_field = forms.CharField(
        label = 'Источник',
        help_text='Источник контактов или название поля в файле',
        required=True
    )

    def save(self):
        super().save()
        extra_fields = [('source_from_table', 'source_name_field', 'source')]
        load_data('RequestContact', f'{MEDIA_ROOT}/data.xlsx', extra_fields, **self.cleaned_data)


class YaContactForm(ContactForm):
    order_amount_name_field = forms.CharField(
        label = 'Кол-во заказов',
        help_text='Кол-во заказов у контакта или название поля в файле',
        required=True
    )

    def save(self):
        super().save()
        extra_fields = [('order_amount_name_field', 'order_amount_name_field', 'order_amount')]
        load_data('YaContact', f'{MEDIA_ROOT}/data.xlsx', extra_fields, **self.cleaned_data)


class LinkedinContactForm(ContactForm):
    profile_link_name_field = forms.CharField(
        label = 'Профиль',
        help_text='Профиль контактов или название поля в файле',
        required=True
    )
    company_field_name_field = forms.CharField(
        label = 'Деятельность компании',
        help_text='Деятельность или название поля в файле',
        required=True
    )

    def save(self):
        super().save()
        extra_fields = [
            ('profile_link_name_field', 'profile_link_name_field', 'profile_link'),
            ('company_field_name_field', 'company_field_name_field', 'company_field'),
        ]
        load_data('LinkedinContact', f'{MEDIA_ROOT}/data.xlsx', extra_fields, **self.cleaned_data)

    
class TsumContactForm(ContactForm):
    name_from_table = forms.BooleanField(
        label='Брать название бредна из файлы',
        help_text='Если не указано, то название бредна будет взято из поля ниже',
        initial=False, required=False
    )
    name_name_field = forms.CharField(
        label = 'Название бредна',
        help_text='Название бредна или название поля в файле',
        required=True
    )

    def save(self):
        super().save()
        extra_fields = [('name_from_table', 'name_name_field', 'name')]
        load_data('TsumContact', f'{MEDIA_ROOT}/data.xlsx', extra_fields, **self.cleaned_data)


class PropertyContactForm(ContactForm):
    name_from_table = forms.BooleanField(
        label='Брать название ЖК из файлы',
        help_text='Если не указано, то название бредна будет взято из поля ниже',
        initial=False, required=False
    )
    name_name_field = forms.CharField(
        label = 'Название ЖК',
        help_text='Название ЖК или название поля в файле',
        required=True
    )

    def save(self):
        super().save()
        extra_fields = [('name_from_table', 'name_name_field', 'name')]
        load_data('PropertyContact', f'{MEDIA_ROOT}/data.xlsx', extra_fields, **self.cleaned_data)

    

class VillageContactForm(ContactForm):
    name_from_table = forms.BooleanField(
        label='Брать название поселка из файлы',
        help_text='Если не указано, то название бредна будет взято из поля ниже',
        initial=False, required=False
    )
    name_name_field = forms.CharField(
        label = 'Название поселка',
        help_text='Название поселка или название поля в файле',
        required=True
    )

    def save(self):
        super().save()
        extra_fields = [('name_from_table', 'name_name_field', 'name')]
        load_data('VillageContact', f'{MEDIA_ROOT}/data.xlsx', extra_fields, **self.cleaned_data)
