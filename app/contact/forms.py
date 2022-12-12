from django import forms
from contact.models import *
from django.core.files.storage import default_storage


class BaseForm(forms.Form):
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
        help_text='В формате cvs или xlsx',
        required=True
    )
    telegram = forms.BooleanField(
        label = 'Есть в Telegram',
        help_text='Все контакты есть в Telegram',
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


class ContactForm(BaseForm):

    def save(self):
        phone_name_filed = self.cleaned_data['phone_name_filed']
        email_name_filed = self.cleaned_data['email_name_filed']
        fio_name_filed = self.cleaned_data['fio_name_filed']

        telegram = self.cleaned_data['telegram']
        whatsapp = self.cleaned_data['whatsapp']
        tg_username_filed = self.cleaned_data['tg_username_filed']
        print(phone_name_filed, email_name_filed)

        