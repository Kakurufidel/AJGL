from django.contrib import admin
from .models import User,Cotisation
from django.utils import timezone
from django.contrib import admin
from django.utils.html import format_html



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

@admin.register(Cotisation)
class CotisationAdmin(admin.ModelAdmin):
    list_display = ('membre', 'type_cotisation', 'montant', 'statut', 'mois', 'evenement', 'date_soumission')
    list_filter = ('type_cotisation', 'statut', 'date_soumission')
    search_fields = ('membre__nom_complet', 'membre__email')
    readonly_fields = ('date_soumission', 'apercu_justificatif')
    
    fieldsets = (
        ('Membre', {'fields': ('membre',)}),
        ('Type de cotisation', {'fields': ('type_cotisation', 'mois', 'evenement')}),
        ('Paiement', {'fields': ('montant', 'justificatif', 'apercu_justificatif')}),
        ('Validation', {'fields': ('statut', 'valide_par', 'date_validation', 'commentaire_rejet')}),
        ('Dates', {'fields': ('date_soumission',)}),
    )
    
    def apercu_justificatif(self, obj):
        if obj.justificatif:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.justificatif.url)
        return "Aucun justificatif"
    apercu_justificatif.short_description = "Aperçu justificatif"
    
    actions = ['valider_cotisations', 'rejeter_cotisations']
    
    def valider_cotisations(self, request, queryset):
        queryset.update(statut='validee', valide_par=request.user, date_validation=timezone.now())
        self.message_user(request, f"{queryset.count()} cotisation(s) validée(s)")
    valider_cotisations.short_description = "Valider les cotisations sélectionnées"
    
    def rejeter_cotisations(self, request, queryset):
        queryset.update(statut='rejetee')
        self.message_user(request, f"{queryset.count()} cotisation(s) rejetée(s)")
    rejeter_cotisations.short_description = "Rejeter les cotisations sélectionnées"