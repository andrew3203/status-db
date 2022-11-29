from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from contact.models import *


class PhoneFilter(SimpleListFilter):
    title = 'Телефон'
    parameter_name = 'obj_phone'

    def lookups(self, request, model_admin):
        return [(1, 'Есть'), (0, 'Нет')]

    def queryset(self, request, queryset):
        if self.value() == 1:
            return queryset.exclude(tel=None)
        elif self.value() == 0:
            return queryset.filter(tel=None)
        else:
            return queryset


class EmailFilter(PhoneFilter):
    title = 'Почта'
    parameter_name = 'obj_mail'

    def queryset(self, request, queryset):
        if self.value() == 1:
            return queryset.exclude(email=None)
        elif self.value() == 0:
            return queryset.filter(email=None)
        else:
            return queryset


LIST_FDISPLAY_DEFAULT = [
    'fio', 'tel', 'email', 'country', 'city', 'task',
    'updated_at', 'created_at', 'whatsapp', 'telegram'
]

SEARCH_FIELDS_DEFAULT = [
    'fio', 'tel', 'email', 'tel2', 'email2',
    'country', 'city', 'addres', 'tg_username'
]

LIST_FILTER_DEFAULT = [
    PhoneFilter, EmailFilter,
    'task', 'telegram', 'whatsapp', 'country', 'city',
]

FIELDSETS_DEFAULT = [
    ('Основное', {
        'fields': (
            ('fio', 'created_at'),
            ('tel', 'email'),
            ('tel2', 'email2'),
            ('country', 'city', 'addres'),
        ),
    }),
    ('', {
        'fields': (
            ('telegram', 'tg_username'),
            ('whatsapp',),
            ('task', 'updated_at')
        ),
    }),
]
READONLY_FIELD_DEFAULT = ('created_at', 'updated_at')


@admin.register(RequestContact)
class RequestContactAdmin(admin.ModelAdmin):
    list_display = LIST_FDISPLAY_DEFAULT
    search_fields = SEARCH_FIELDS_DEFAULT
    list_filter = LIST_FILTER_DEFAULT

    fieldsets = FIELDSETS_DEFAULT
    readonly_fields = READONLY_FIELD_DEFAULT


@admin.register(YaContact)
class YaContactAdmin(admin.ModelAdmin):
    list_display = LIST_FDISPLAY_DEFAULT + ['order_amount']
    search_fields = SEARCH_FIELDS_DEFAULT
    list_filter = LIST_FILTER_DEFAULT
    
    fieldsets = FIELDSETS_DEFAULT + \
        [('', {
            'fields': (
                ('order_amount',),
                ),
            }
        )]
    readonly_fields = READONLY_FIELD_DEFAULT


@admin.register(LinkedinContact)
class LinkedinContactAdmin(admin.ModelAdmin):
    list_display = LIST_FDISPLAY_DEFAULT + ['profile_link']
    search_fields = SEARCH_FIELDS_DEFAULT
    list_filter = LIST_FILTER_DEFAULT
    
    fieldsets = FIELDSETS_DEFAULT + \
        [('', {
            'fields': (
                ('profile_link',),
                ),
            }
        )]
    readonly_fields = READONLY_FIELD_DEFAULT


@admin.register(TsumContact)
class TsumContactAdmin(admin.ModelAdmin):
    list_display = LIST_FDISPLAY_DEFAULT + ['name']
    search_fields = SEARCH_FIELDS_DEFAULT + ['name']
    list_filter = LIST_FILTER_DEFAULT + ['name']
    
    fieldsets = FIELDSETS_DEFAULT + \
        [('', {
            'fields': (
                ('name',),
                ),
            }
        )]
    readonly_fields = READONLY_FIELD_DEFAULT


@admin.register(PropertyContact)
class TsumContactAdmin(admin.ModelAdmin):
    list_display = LIST_FDISPLAY_DEFAULT + ['company_field', 'name']
    search_fields = SEARCH_FIELDS_DEFAULT + ['company_field', 'name']
    list_filter = LIST_FILTER_DEFAULT + ['company_field', 'name']
    
    fieldsets = FIELDSETS_DEFAULT + \
        [('', {
            'fields': (
                ('name', 'company_field',),
                ),
            }
        )]
    readonly_fields = READONLY_FIELD_DEFAULT


@admin.register(VillageContact)
class VillageContactAdmin(admin.ModelAdmin):
    list_display = LIST_FDISPLAY_DEFAULT + ['name']
    search_fields = SEARCH_FIELDS_DEFAULT + ['name']
    list_filter = LIST_FILTER_DEFAULT + ['name']
    
    fieldsets = FIELDSETS_DEFAULT + \
        [('', {
            'fields': (
                ('name',),
                ),
            }
        )]
    readonly_fields = READONLY_FIELD_DEFAULT


admin.site.site_header = 'STATUS Админ панель'
admin.site.site_title = 'Панель администратора STATUS'
admin.site.index_title = 'Администратор'
