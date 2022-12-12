from django.db import models


class TaskType(models.TextChoices):
    MAILING = 'MAILING', 'Почта'
    WH = 'WH', 'WhatsApp'
    TG = 'Tg', 'Telegramm'
    YANDEX = 'YANDEX', 'Яндекс'
    FB = 'FB', 'Facebook'
    INST = 'INST', 'Instagram'
    GOOGLE = 'GOOGLE', 'Google'
    

class Contact(models.Model):
    fio = models.CharField(
        verbose_name = 'ФИО',
        max_length=512, 
        default='Пользователь', blank=True
    )
    tel = models.CharField(
        verbose_name = 'Телефон',
        max_length=20,
        default=None, blank=True, null=True
    )
    email = models.CharField(
        verbose_name = 'Почта',
        max_length=50,
        default=None, blank=True, null=True
    )
    tel2 = models.CharField(
        verbose_name = 'Доп. Телефон',
        max_length=20,
        default=None, blank=True, null=True
    )
    email2 = models.CharField(
        verbose_name = 'Доп. Почта',
        max_length=20,
        default=None, blank=True, null=True
    )

    telegram = models.BooleanField(
        verbose_name = 'Есть в TG',
        default=False
    )
    tg_username = models.CharField(
        verbose_name = 'Телеграм',
        max_length=20,
        default=None, blank=True, null=True
    )

    whatsapp = models.BooleanField(
        verbose_name = 'Есть в WH',
        default=False
    )

    country = models.CharField(
        verbose_name = 'Страна',
        max_length=50,
        default=None, blank=True, null=True
    )
    city = models.CharField(
        verbose_name = 'Город',
        max_length=512,
        default=None, blank=True, null=True
    )
    addres = models.CharField(
        verbose_name = 'Аддерс',
        max_length=512,
        default=None, blank=True, null=True
    )

    created_at = models.DateTimeField(
        'Добавлен',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Изменен',
        auto_now=True, 
    )
    task = models.CharField(
        'Задача',
        max_length=25,
        choices=TaskType.choices,
        default=None, blank=True, null=True
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.fio


class RequestContact(Contact):
    source = models.CharField(
        verbose_name = 'Источник',
        max_length=512,
        blank=True, null=True
    )
    
    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'База заявок'


class BrockerContact(Contact):
    notice = models.TextField(
        verbose_name = 'Заметка',
        max_length=512
    )

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Брокерские базы'


class YaContact(Contact):
    order_amount = models.FloatField(
        verbose_name = 'Сумма заказов',
        default=0, blank=True, null=True
    )

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'База Яндекс'

class LinkedinContact(Contact):
    profile_link = models.CharField(
        verbose_name = 'Профиль',
        max_length=512
    )

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'База Linkedin'


class TsumContact(Contact):
    name = models.CharField(
        verbose_name = 'Название бренда',
        max_length=512,
        blank=True, null=True
    )

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'База ЦУМ'

class PropertyContact(Contact):
    name = models.CharField(
        verbose_name = 'Название ЖК',
        max_length=512
    )
    company_field = models.CharField(
        verbose_name = 'Деятельность',
        max_length=512,
        blank=True, null=True
    )

    class Meta: 
        verbose_name = 'Контакт'
        verbose_name_plural = 'База ЖК'


class VillageContact(Contact):
    name = models.CharField(
        verbose_name = 'Название поселка',
        max_length=512,
        blank=True, null=True
    )
    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'База Загород'

