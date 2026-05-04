from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, nom_complet, telephone, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'adresse email est obligatoire')
        if not nom_complet:
            raise ValueError('Le nom complet est obligatoire')
        if not telephone:
            raise ValueError('Le numéro de téléphone est obligatoire')
        
        email = self.normalize_email(email)
        user = self.model(email=email, nom_complet=nom_complet, telephone=telephone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, nom_complet, telephone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(email, nom_complet, telephone, password, **extra_fields)

# ==========================================
# MODÈLE USER (MEMBRE) – AUTHENTIFICATION PAR EMAIL
# ==========================================

class User(AbstractUser):
    
    username = None  # Désactiver le champ username
    email = models.EmailField(unique=True)  # Email comme identifiant principal
    
    # Choix pour les listes déroulantes
    ROLES = [
    ('parent', 'Parent'),
    ('jumeau', 'Jumeau'),
    ('jumelle', 'Jumelle'),
    ]
    
    ETAT_CIVIL = [
        ('celibataire', 'Célibataire'),
        ('marie', 'Marié(e)'),
        ('divorce', 'Divorcé(e)'),
        ('veuf', 'Veuf/Veuve'),
    ]
    
    STATUT_PRO = [
        ('etudiant', 'Étudiant'),
        ('salarie', 'Salarié'),
        ('independant', 'Indépendant'),
        ('sans_emploi', 'Sans emploi'),
        ('autre', 'Autre'),
    ]
    
    PAYS = [
        ('RDC', 'République Démocratique du Congo'),
        ('Rwanda', 'Rwanda'),
        ('Burundi', 'Burundi'),
    ]
    
    # Champs principaux obligatoires
    nom_complet = models.CharField(max_length=100)
    adresse = models.TextField(help_text="Commune, Quartier, Avenue")
    pays = models.CharField(max_length=20, choices=PAYS, default='RDC')
    ville = models.CharField(max_length=100, blank=True, null=True, help_text="Ex: Goma, Bukavu, Bujumbura, Kigali")
    telephone = models.CharField(max_length=20)
    
    # Champs pour les jumeaux
    noms_jumeaux_lies = models.TextField(blank=True, null=True, help_text="Noms des jumeaux/triplés (séparés par des virgules)")
    
    # Champs pour les parents
    nom_papa = models.CharField(max_length=100, blank=True, null=True)
    nom_maman = models.CharField(max_length=100, blank=True, null=True)
    etat_civil = models.CharField(max_length=20, choices=ETAT_CIVIL, blank=True, null=True)
    statut_pro = models.CharField(max_length=20, choices=STATUT_PRO, blank=True, null=True)
    
    # Photo et rôles
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    type_roles = models.CharField(max_length=50, blank=True, default='', help_text="parent,jumeau ou parent ou jumeau")
    
    # Date d'inscription
    date_inscription = models.DateTimeField(auto_now_add=True)
    
    
    objects =CustomUserManager()
    # Configuration pour l'authentification par email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom_complet', 'telephone']
    
    def __str__(self):
        return f"{self.nom_complet} ({self.get_pays_display()})"
    
    def get_roles_list(self):
        return self.type_roles.split(',') if self.type_roles else []
    
    class Meta:
        ordering = ['-date_inscription']
        verbose_name = "Membre"
        verbose_name_plural = "Membres"
        


# ==========================================
# MODÈLE COTISATION (avec validation coordinateur)
# ==========================================

class Cotisation(models.Model):
    TYPE_CHOICES = [
        ('mensuelle', 'Cotisation mensuelle'),
        ('speciale', 'Cotisation spéciale (activité)'),
    ]
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente de validation'),
        ('validee', 'Validée'),
        ('rejetee', 'Rejetée'),
    ]
    
    PERIODE_CHOICES = [
        ('mensuelle', 'Mensuelle'),
        ('annuelle', 'Annuelle'),
    ]
    
    # Liens
    membre = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Membre")
    
    # Type de cotisation
    type_cotisation = models.CharField(max_length=20, choices=TYPE_CHOICES, default='mensuelle')
    
    # Pour cotisation mensuelle
    mois = models.DateField(null=True, blank=True, help_text="Premier jour du mois (ex: 2026-05-01)")
    
    # Pour cotisation spéciale (liée à une activité)
    evenement = models.ForeignKey('Evenement', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Événement lié")
    
    # Montant
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant (€)")
    periode = models.CharField(max_length=20, choices=PERIODE_CHOICES, default='mensuelle', verbose_name="Périodicité")
    
    # Paiement
    methode_paiement = models.CharField(max_length=50, blank=True, null=True, verbose_name="Méthode de paiement")
    justificatif = models.ImageField(upload_to='justificatifs/', blank=True, null=True, verbose_name="Capture écran paiement")
    
    # Validation
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    valide_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='validations', verbose_name="Validé par")
    date_validation = models.DateTimeField(null=True, blank=True, verbose_name="Date de validation")
    commentaire_rejet = models.TextField(blank=True, null=True, verbose_name="Motif du rejet")
    
    # Dates
    date_debut = models.DateField(null=True, blank=True, verbose_name="Date de début")
    date_fin = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    date_paiement = models.DateTimeField(null=True, blank=True, verbose_name="Date de paiement")
    date_soumission = models.DateTimeField(auto_now_add=True, verbose_name="Date de soumission")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    # Notification
    notification_envoyee = models.BooleanField(default=False, verbose_name="Notification envoyée")
    
    # ==========================================
    # LOGIQUE MÉTIER
    # ==========================================
    
    def clean(self):
        if self.montant and self.montant <= 0:
            raise ValidationError({'montant': "Le montant doit être supérieur à 0€"})
        
        if self.date_debut and self.date_fin and self.date_fin <= self.date_debut:
            raise ValidationError({'date_fin': "La date de fin doit être postérieure à la date de début"})
    
    def save(self, *args, **kwargs):
        if self.statut == 'validee' and not self.date_validation:
            from django.utils import timezone
            self.date_validation = timezone.now()
        self.full_clean()
        super().save(*args, **kwargs)
    
    def est_actif(self):
        from django.utils import timezone
        if self.statut == 'validee' and self.date_fin:
            return self.date_fin >= timezone.now().date()
        return False
    
    def __str__(self):
        return f"{self.membre.nom_complet} - {self.get_type_cotisation_display()} - {self.montant}€ - {self.get_statut_display()}"
    
    class Meta:
        ordering = ['-date_soumission']
        verbose_name = "Cotisation"
        verbose_name_plural = "Cotisations"


# ==========================================
# MODÈLE ÉVÉNEMENT
# ==========================================

class Evenement(models.Model):
    TYPE_EVENEMENT = [
        ('formation', 'Formation professionnelle'),
        ('apostolat', 'Apostolat / Visite sociale'),
        ('exposition', 'Exposition culturelle et artistique'),
        ('culturel', 'Activité culturelle'),
        ('sportif', 'Activité sportive (match de football)'),
        ('celebration', 'Célébration / Anniversaire'),
        ('assistance', 'Assistance humanitaire'),
        ('reunion', 'Réunion / Assemblée'),
        ('autre', 'Autre'),
    ]
    
    STATUT_EVENEMENT = [
        ('a_venir', 'À venir'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ]
    
    titre = models.CharField(max_length=200, verbose_name="Titre de l'événement")
    type_event = models.CharField(max_length=50, choices=TYPE_EVENEMENT, verbose_name="Type d'événement")
    description = models.TextField(verbose_name="Description")
    
    date_debut = models.DateTimeField(verbose_name="Date de début")
    date_fin = models.DateTimeField(blank=True, null=True, verbose_name="Date de fin")
    lieu = models.CharField(max_length=200, verbose_name="Lieu")
    
    image = models.ImageField(upload_to='evenements/', blank=True, null=True, verbose_name="Image principale")
    galerie_images = models.TextField(blank=True, null=True, help_text="URLs des images supplémentaires (séparées par des virgules)")
    
    nombre_participants = models.IntegerField(default=0, verbose_name="Nombre de participants")
    nombre_jumeaux_present = models.IntegerField(default=0, verbose_name="Nombre de jumeaux présents")
    nombre_parents_present = models.IntegerField(default=0, verbose_name="Nombre de parents présents")
    
    statut = models.CharField(max_length=20, choices=STATUT_EVENEMENT, default='a_venir', verbose_name="Statut")
    est_visible_site = models.BooleanField(default=True, verbose_name="Afficher sur le site")
    
    compte_rendu = models.TextField(blank=True, null=True, verbose_name="Compte-rendu / Résultats")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    def save(self, *args, **kwargs):
        from django.utils import timezone
        if self.date_debut > timezone.now():
            self.statut = 'a_venir'
        elif self.date_debut <= timezone.now() and (not self.date_fin or self.date_fin >= timezone.now()):
            self.statut = 'en_cours'
        elif self.date_fin and self.date_fin < timezone.now():
            self.statut = 'termine'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.titre} - {self.date_debut.strftime('%d/%m/%Y')}"
    
    class Meta:
        ordering = ['-date_debut']
        verbose_name = "Événement"
        verbose_name_plural = "Événements"


# ==========================================
# MODÈLE ACTUALITÉ
# ==========================================

class Actualite(models.Model):
    CATEGORIE_ACTUALITE = [
        ('annonce', 'Annonce officielle'),
        ('evenement', 'Retour sur événement'),
        ('temoignage', 'Témoignage'),
        ('partenariat', 'Partenariat'),
        ('appel', 'Appel à participation'),
        ('autre', 'Autre'),
    ]
    
    titre = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL personnalisée")
    contenu = models.TextField(verbose_name="Contenu")
    extrait = models.TextField(blank=True, null=True, max_length=300, verbose_name="Extrait (résumé)")
    categorie = models.CharField(max_length=50, choices=CATEGORIE_ACTUALITE, default='annonce', verbose_name="Catégorie")
    
    image_principale = models.ImageField(upload_to='actualites/', blank=True, null=True, verbose_name="Image principale")
    
    est_publie = models.BooleanField(default=True, verbose_name="Publié ?")
    date_publication = models.DateTimeField(auto_now_add=True, verbose_name="Date de publication")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    evenement_lie = models.ForeignKey(Evenement, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Événement lié")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            import re
            self.slug = re.sub(r'[^a-z0-9]+', '-', self.titre.lower()).strip('-')
        super().save(*args, **kwargs)
    
    def get_extrait(self):
        if self.extrait:
            return self.extrait
        if len(self.contenu) > 150:
            return self.contenu[:150] + "..."
        return self.contenu
    
    def __str__(self):
        return self.titre
    
    class Meta:
        ordering = ['-date_publication']
        verbose_name = "Actualité"
        verbose_name_plural = "Actualités"


# ==========================================
# MODÈLE PARTENAIRE (optionnel)
# ==========================================

class Partenaire(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom du partenaire")
    logo = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name="Logo")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    pays = models.CharField(max_length=50, blank=True, null=True, verbose_name="Pays")
    site_web = models.URLField(blank=True, null=True, verbose_name="Site web")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    
    def __str__(self):
        return self.nom
    
    class Meta:
        ordering = ['nom']
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"


# ==========================================
# MODÈLE CELLULE (optionnel)
# ==========================================

class Cellule(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom de la cellule")
    quartier = models.CharField(max_length=100, verbose_name="Quartier")
    ville = models.CharField(max_length=100, verbose_name="Ville")
    pays = models.CharField(max_length=50, verbose_name="Pays")
    responsable = models.CharField(max_length=100, verbose_name="Nom du responsable")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone du responsable")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    def __str__(self):
        return f"{self.nom} - {self.quartier}"
    
    class Meta:
        ordering = ['pays', 'ville', 'quartier']
        verbose_name = "Cellule"
        verbose_name_plural = "Cellules"