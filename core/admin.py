from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('nom_complet', 'email', 'telephone', 'type_roles', 'date_inscription')
    list_filter = ('type_roles', 'date_inscription')
    search_fields = ('nom_complet', 'email')
    readonly_fields = ('date_inscription',)