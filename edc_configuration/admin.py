from django.contrib import admin


from .models import GlobalConfiguration


class GlobalConfigurationAdmin(admin.ModelAdmin):
    list_display = ('category', 'attribute', 'value', 'convert')
    list_filter = ('category', )
    search_fields = ('attribute', 'category', 'attribute', 'value')
admin.site.register(GlobalConfiguration, GlobalConfigurationAdmin)
