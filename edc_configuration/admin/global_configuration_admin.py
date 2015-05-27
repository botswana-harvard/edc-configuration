from django.contrib import admin

from edc_base.modeladmin.admin import BaseModelAdmin

from ..models import GlobalConfiguration


class GlobalConfigurationAdmin(BaseModelAdmin):
    list_display = ('category', 'attribute', 'value', 'convert')
    list_filter = ('category', )
    search_fields = ('attribute', 'category', 'attribute', 'value')
admin.site.register(GlobalConfiguration, GlobalConfigurationAdmin)
