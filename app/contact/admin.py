from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponse, FileResponse
from django.shortcuts import render
from django.urls import reverse
from admin_extra_buttons.api import ExtraButtonsMixin, button, confirm_action, link, view
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin import SimpleListFilter
from contact.models import *
from contact.forms import *
from contact.uploader import _get_csv_from_qs_values


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
btr_args = {'change_form': True, 'html_attrs': {'style': 'background-color:#ff9966;color:black'}, 'label' : 'Импортировать контакты'}

def _upload(self, request):
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        print(request.FILES)
        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                self.message_user(request, e)
                return render(request, 'admin/upload.html', {'form': form})

            self.message_user(request, 'Контакты успешно ипортированы!')
            url = reverse(self.URL)
            return HttpResponseRedirect(url)

        else:
            return render(request, 'admin/upload.html', {'form': form})

    else:
        form = ContactForm()
        return render(request, 'admin/upload.html', {'form': form})



@admin.register(RequestContact)
class RequestContactAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = LIST_FDISPLAY_DEFAULT + ['source']
    search_fields = SEARCH_FIELDS_DEFAULT
    list_filter = LIST_FILTER_DEFAULT

    fieldsets = FIELDSETS_DEFAULT+ \
        [('', {
            'fields': (
                ('source',),
                ),
            }
        )]
    
    readonly_fields = READONLY_FIELD_DEFAULT
    URL = f'admin:{RequestContact._meta.app_label}_{RequestContact._meta.model_name}_changelist'

    @button(**btr_args)
    def upload(self, request):
        return _upload(self, request)

    def download(self, request, queryset):
        file, filename = _get_csv_from_qs_values(queryset.values())
        return FileResponse(file, filename=filename)

    actions = [download]
    download.short_description = 'Выгрузить контакты'


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
