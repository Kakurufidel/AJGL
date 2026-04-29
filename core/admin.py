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
    from .models import Cotisation

@admin.register(Cotisation)
class CotisationAdmin(admin.ModelAdmin):
    list_display = ('id', 'membre', 'montant', 'periode', 'statut', 'date_debut', 'date_fin', 'est_actif_display')
    list_filter = ('statut', 'periode', 'date_debut')
    search_fields = ('membre__nom_complet', 'membre__email', 'reference_paiement')
    readonly_fields = ('date_creation',)
    
    fieldsets = (
        ('Membre', {
            'fields': ('membre',)
        }),
        ('Cotisation', {
            'fields': ('montant', 'periode', 'statut', 'date_debut', 'date_fin')
        }),
        ('Paiement', {
            'fields': ('methode_paiement', 'reference_paiement', 'date_paiement', 'commentaire')
        }),
        ('Dates système', {
            'fields': ('date_creation',),
            'classes': ('collapse',)
        }),
    )
    
    def est_actif_display(self, obj):
        return "✅ Actif" if obj.est_actif() else "❌ Inactif"
    est_actif_display.short_description = "Statut validité"
    
    actions = ['marquer_comme_paye']
    
    def marquer_comme_paye(self, request, queryset):
        from django.utils import timezone
        queryset.update(statut='paye', date_paiement=timezone.now())
        self.message_user(request, f"{queryset.count()} cotisation(s) marquée(s) comme payée(s)")
    marquer_comme_paye.short_description = "Marquer comme payé"