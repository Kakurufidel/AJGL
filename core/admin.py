from django.contrib import admin
from django.utils.html import format_html
from .models import User, Cotisation, Contribution, Evenement, Actualite, Partenaire, Cellule


# ==========================================
# ADMIN USER (MEMBRE)
# ==========================================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'nom_complet', 'telephone', 'pays', 'ville', 'is_staff', 'date_joined')
    list_display_links = ('email', 'nom_complet')
    list_filter = ('pays', 'is_staff', 'is_active')
    search_fields = ('email', 'nom_complet', 'telephone')
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        ('Identifiants', {
            'fields': ('email', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('nom_complet', 'telephone', 'pays', 'ville', 'adresse', 'photo')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Dates', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 50%;" />', obj.photo.url)
        return "-"
    photo_preview.short_description = "Photo"


# ==========================================
# ADMIN COTISATION
# ==========================================

@admin.register(Cotisation)
class CotisationAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'type', 'date_debut', 'date_fin', 'statut')
    list_filter = ('type', 'statut', 'obligatoire')
    search_fields = ('titre', 'numero_paiement')
    readonly_fields = ('date_creation',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'description', 'type', 'montant', 'obligatoire')
        }),
        ('Période de validité', {
            'fields': ('date_debut', 'date_fin')
        }),
        ('Informations bancaires', {
            'fields': ('numero_paiement', 'nom_beneficiaire')
        }),
        ('Validation', {
            'fields': ('statut', 'cree_par', 'valide_par', 'date_validation')
        }),
        ('Dates', {
            'fields': ('date_creation',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['valider_cotisations']
    
    def valider_cotisations(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(statut='valide', date_validation=timezone.now())
        self.message_user(request, f"{updated} cotisation(s) validée(s)")
    valider_cotisations.short_description = "Valider les cotisations sélectionnées"


# ==========================================
# ADMIN CONTRIBUTION (PAIEMENT)
# ==========================================

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('id', 'membre', 'cotisation', 'montant', 'statut', 'date_creation')
    list_filter = ('statut', 'date_creation')
    search_fields = ('membre__nom_complet', 'membre__email', 'cotisation__titre')
    readonly_fields = ('date_creation', 'preview_preuve')
    
    fieldsets = (
        ('Membre et cotisation', {
            'fields': ('membre', 'cotisation')
        }),
        ('Détails du paiement', {
            'fields': ('montant', 'preuve_paiement', 'preview_preuve')
        }),
        ('Validation', {
            'fields': ('statut', 'commentaire', 'valide_par', 'date_validation')
        }),
        ('Dates', {
            'fields': ('date_creation',),
            'classes': ('collapse',)
        }),
    )
    
    def preview_preuve(self, obj):
        if obj.preuve_paiement:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="max-height: 100px; max-width: 100px;" /></a>', obj.preuve_paiement.url, obj.preuve_paiement.url)
        return "-"
    preview_preuve.short_description = "Aperçu preuve"
    
    actions = ['valider_contributions', 'rejeter_contributions']
    
    def valider_contributions(self, request, queryset):
        from django.utils import timezone
        updated = 0
        for contribution in queryset:
            if contribution.statut != 'valide':
                contribution.valider(request.user)
                updated += 1
        self.message_user(request, f"{updated} contribution(s) validée(s)")
    valider_contributions.short_description = "Valider les contributions sélectionnées"
    
    def rejeter_contributions(self, request, queryset):
        updated = queryset.update(statut='rejetee')
        self.message_user(request, f"{updated} contribution(s) rejetée(s)")
    rejeter_contributions.short_description = "Rejeter les contributions sélectionnées"


# ==========================================
# ADMIN ÉVÉNEMENT
# ==========================================

@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'date_debut', 'lieu', 'statut')
    list_filter = ('statut', 'date_debut')
    search_fields = ('titre', 'lieu', 'description')
    readonly_fields = ('date_creation',)


# ==========================================
# ADMIN ACTUALITÉ
# ==========================================

@admin.register(Actualite)
class ActualiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'categorie', 'est_publie', 'date_publication')
    list_filter = ('categorie', 'est_publie', 'date_publication')
    search_fields = ('titre', 'contenu')
    prepopulated_fields = {'slug': ('titre',)}
    readonly_fields = ('date_publication', 'date_modification')


# ==========================================
# ADMIN PARTENAIRE
# ==========================================

@admin.register(Partenaire)
class PartenaireAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'pays', 'est_actif', 'ordre_affichage')
    list_filter = ('pays', 'est_actif')
    search_fields = ('nom', 'description')
    list_editable = ('ordre_affichage', 'est_actif')


# ==========================================
# ADMIN CELLULE
# ==========================================

@admin.register(Cellule)
class CelluleAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'quartier', 'ville', 'pays', 'responsable', 'est_active')
    list_filter = ('pays', 'ville', 'est_active')
    search_fields = ('nom', 'quartier', 'responsable')