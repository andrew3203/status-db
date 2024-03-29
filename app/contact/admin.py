from django.contrib import admin
from django.http import HttpResponseRedirect, FileResponse, StreamingHttpResponse
from django.shortcuts import render
from django.urls import reverse
from admin_extra_buttons.api import ExtraButtonsMixin, button
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from django.contrib.admin import SimpleListFilter
from contact.models import *
from contact.forms import *
from contact.uploader import _get_xlsx_from_qs_values
from django.contrib import messages
from django_celery_beat.models import PeriodicTask, IntervalSchedule, SolarSchedule, CrontabSchedule, ClockedSchedule


admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(ClockedSchedule)


class PhoneFilter(SimpleListFilter):
    title = 'Телефон'
    parameter_name = 'obj_phone'

    def lookups(self, request, model_admin):
        return (('1', 'Есть'), ('0', 'Нет'))

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(tel__isnull = False).exclude(tel='')
        elif self.value() == '0':
            return queryset.filter(tel__isnull = True)
        else:
            return queryset


class EmailFilter(SimpleListFilter):
    title = 'Почта'
    parameter_name = 'obj_mail'

    def lookups(self, request, model_admin):
        return (('1', 'Есть'), ('0', 'Нет'))

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(email__isnull=False).exclude(email='')
        elif self.value() == '0':
            return queryset.filter(email__isnull=True)
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
            ('whatsapp', 'telegram', 'tg_username'),
            ('task', 'updated_at')
        ),
    }),
]
READONLY_FIELD_DEFAULT = ('created_at', 'updated_at')
btr_args = {'change_form': True, 'html_attrs': {'style': 'background-color:#ff9966;color:black'}, 'label' : 'Импортировать контакты'}
btr_args2 = {'change_form': True, 'html_attrs': {'style': 'background-color:#88FF88;color:black'}, 'label' : 'Обновить страницу'}
btr_args3 = {'change_form': True, 'html_attrs': {'style': 'background-color:#34ebeb;color:black'}, 'label' : 'Telegram/WhatsApp'}


def _upload(self, request, FormClass):
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                print(e)
                self.message_user(request, e, level=messages.ERROR)
                return render(request, 'admin/upload.html', {'form': form})

            self.message_user(request, 'Ипморт контактов запущен!')
            return HttpResponseRedirect(reverse(self.URL))
        else:
            return render(request, 'admin/upload.html', {'form': form})
    else:
        form = FormClass()
        return render(request, 'admin/upload.html', {'form': form})

def _load_wh_tg(self, request, instance_str):
    if request.method == 'POST':
        form = LoadTgWhForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                print(e)
                self.message_user(request, e, level=messages.ERROR)
                return render(request, 'admin/load_wh_tg.html', {'form': form})

            self.message_user(request, f'Загрузка запущена')
            return HttpResponseRedirect(reverse(self.URL))
        else:
            return render(request, 'admin/load_wh_tg.html', {'form': form})
    else:
        form = LoadTgWhForm(initial={'_instance_str': instance_str })
        return render(request, "admin/load_wh_tg.html", {'form': form})



class BaseContact(ExtraButtonsMixin, admin.ModelAdmin):
   
    @button(**btr_args2)
    def refresh(self, request):
        self.message_user(request, 'Страница обновлена')
        return HttpResponseRedirectToReferrer(request)

    def download(self, request, queryset):
        file, filename = _get_xlsx_from_qs_values(queryset.values())
        #return FileResponse(file, filename=filename)
        response = StreamingHttpResponse(file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
    
    def set_task(self, request, queryset):
        if 'apply' in request.POST:
            num = SetTaskForm(request.POST).save()
            model_name = queryset.model._meta.model_name
            self.message_user(request, f'Задача для {num} контактов присвоена!')
            return HttpResponseRedirect(reverse(f'admin:contact_{model_name}_changelist'))
        else:
            contact_ids = list(queryset.values_list('pk', flat=True))
            print(len(contact_ids))
            instance_str = queryset.model.__name__
            form =  SetTaskForm(initial={'_selected_action': contact_ids, '_instance_str': instance_str })
            return render(request, "admin/task_type.html", {'form': form})

    actions = [download, set_task]
    download.short_description = 'Выгрузить контакты'
    set_task.short_description = 'Назначить задачу'


@admin.register(RequestContact)
class RequestContactAdmin(BaseContact):
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

    @button(**btr_args3)
    def load_wh_tg(self, request):
        return _load_wh_tg(self, request, 'RequestContact')

    @button(**btr_args)
    def upload(self, request):
        return _upload(self, request, RequestContactForm)


@admin.register(YaContact)
class YaContactAdmin(BaseContact):
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
    URL = f'admin:{YaContact._meta.app_label}_{YaContact._meta.model_name}_changelist'

    @button(**btr_args3)
    def load_wh_tg(self, request):
        return _load_wh_tg(self, request, 'YaContact')

    @button(**btr_args)
    def upload(self, request):
        return _upload(self, request, YaContactForm)


@admin.register(LinkedinContact)
class LinkedinContactAdmin(BaseContact):
    list_display = LIST_FDISPLAY_DEFAULT + ['profile_link', 'company_field']
    search_fields = SEARCH_FIELDS_DEFAULT + ['company_field']
    list_filter = LIST_FILTER_DEFAULT + ['company_field']
    
    fieldsets = FIELDSETS_DEFAULT + \
        [('', {
            'fields': (
                ('profile_link', 'company_field'),
                ),
            }
        )]
    readonly_fields = READONLY_FIELD_DEFAULT
    URL = f'admin:{LinkedinContact._meta.app_label}_{LinkedinContact._meta.model_name}_changelist'

    @button(**btr_args3)
    def load_wh_tg(self, request):
        return _load_wh_tg(self, request, 'LinkedinContact')

    @button(**btr_args)
    def upload(self, request):
        return _upload(self, request, LinkedinContactForm)
    

@admin.register(TsumContact)
class TsumContactAdmin(BaseContact):
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
    URL = f'admin:{TsumContact._meta.app_label}_{TsumContact._meta.model_name}_changelist'

    @button(**btr_args3)
    def load_wh_tg(self, request):
        return _load_wh_tg(self, request, 'TsumContact')

    @button(**btr_args)
    def upload(self, request):
        return _upload(self, request, TsumContactForm)
    

@admin.register(PropertyContact)
class PropertyContactAdmin(BaseContact):
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
    URL = f'admin:{PropertyContact._meta.app_label}_{PropertyContact._meta.model_name}_changelist'

    @button(**btr_args3)
    def load_wh_tg(self, request):
        return _load_wh_tg(self, request, 'PropertyContact')

    @button(**btr_args)
    def upload(self, request):
        return _upload(self, request, PropertyContactForm)


@admin.register(VillageContact)
class VillageContactAdmin(BaseContact):
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
    URL = f'admin:{VillageContact._meta.app_label}_{VillageContact._meta.model_name}_changelist'

    @button(**btr_args3)
    def load_wh_tg(self, request):
        return _load_wh_tg(self, request, 'VillageContact')

    @button(**btr_args)
    def upload(self, request):
        return _upload(self, request, VillageContactForm)



admin.site.site_header = 'STATUS Админ панель'
admin.site.site_title = 'Панель администратора STATUS'
admin.site.index_title = 'Администратор'
