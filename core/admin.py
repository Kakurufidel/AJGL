from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('nom_complet', 'email', 'pays', 'ville', 'telephone', 'type_roles', 'date_inscription')
    list_filter = ('pays', 'type_roles', 'date_inscription')
    search_fields = ('nom_complet', 'email', 'ville')
    readonly_fields = ('date_inscription',)
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom_complet', 'email', 'telephone', 'pays', 'ville', 'adresse')
        }),
        ('Rôles', {
            'fields': ('type_roles',)
        }),
        ('Pour les jumeaux/jumelles', {
            'fields': ('noms_jumeaux_lies',),
            'classes': ('collapse',)
        }),
        ('Pour les parents', {
            'fields': ('nom_papa', 'nom_maman', 'etat_civil', 'statut_pro'),
            'classes': ('collapse',)
        }),
        ('Photo', {
            'fields': ('photo',),
            'classes': ('collapse',)
        }),
    )