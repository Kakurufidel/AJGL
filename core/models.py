from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


# ==========================================
# MODÈLE USER (MEMBRE)
# ==========================================

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class User(AbstractUser):
    # Supprimer le champ username par défaut pour utiliser email à la place
    username = None
    # Remplacer par email comme identifiant principal
    email = models.EmailField(unique=True)
    
    # Champs supplémentaires pour l'association
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
    
    # Champs personnalisés
    nom_complet = models.CharField(max_length=100)
    adresse = models.TextField(help_text="Commune, Quartier, Avenue")
    pays = models.CharField(max_length=20, choices=PAYS, default='RDC')
    ville = models.CharField(max_length=100, blank=True, null=True)
    telephone = models.CharField(max_length=20)
    
    noms_jumeaux_lies = models.TextField(blank=True, null=True)
    nom_papa = models.CharField(max_length=100, blank=True, null=True)
    nom_maman = models.CharField(max_length=100, blank=True, null=True)
    etat_civil = models.CharField(max_length=20, choices=ETAT_CIVIL, blank=True, null=True)
    statut_pro = models.CharField(max_length=20, choices=STATUT_PRO, blank=True, null=True)
    
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    type_roles = models.CharField(max_length=50, help_text="parent,jumeau ou parent ou jumeau")
    
    date_inscription = models.DateTimeField(auto_now_add=True)
    
    # Utiliser l'email comme identifiant
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom_complet', 'telephone']
    
    def clean(self):
        if self.pk is None:
            existing_user = User.objects.filter(nom_complet__iexact=self.nom_complet).first()
            if existing_user:
                raise ValidationError({
                    'nom_complet': f"Un membre nommé '{self.nom_complet}' est déjà inscrit."
                })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nom_complet} ({self.get_pays_display()})"
    
    def get_roles_list(self):
        return self.type_roles.split(',')
    
    class Meta:
        ordering = ['-date_inscription']
        verbose_name = "Membre"
        verbose_name_plural = "Membres"
# ==========================================
# MODÈLE DON
# ==========================================

class Don(models.Model):
    METHODES_PAIEMENT = [
        ('mobile_money', 'Mobile Money'),
        ('especes', 'Espèces'),
        ('virement', 'Virement bancaire'),
        ('autre', 'Autre'),
    ]
    
    # Informations du donateur
    nom_complet = models.CharField(max_length=100, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Email")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone")
    
    # Si le donateur est déjà membre
    est_membre = models.BooleanField(default=False, verbose_name="Est membre de l'association ?")
    lien_membre = models.ForeignKey(
        'User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Membre (si déjà inscrit)"
    )
    
    # Informations sur le don
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant (€)")
    methode_paiement = models.CharField(max_length=50, choices=METHODES_PAIEMENT, verbose_name="Méthode de paiement")
    message = models.TextField(blank=True, null=True, verbose_name="Message (optionnel)")
    date_don = models.DateTimeField(auto_now_add=True, verbose_name="Date du don")
    
    # ==========================================
    # VALIDATIONS
    # ==========================================
    
    def clean(self):
        from django.core.validators import validate_email
        
        if self.montant <= 0:
            raise ValidationError({'montant': "Le montant doit être supérieur à 0€"})
        
        if self.montant > 10000:
            raise ValidationError({'montant': "Pour un don supérieur à 10.000€, contactez-nous"})
        
        chiffres = ''.join(filter(str.isdigit, self.telephone))
        if len(chiffres) < 8:
            raise ValidationError({'telephone': "Le téléphone doit contenir au moins 8 chiffres"})
        
        if self.est_membre and not self.lien_membre:
            raise ValidationError({'lien_membre': "Veuillez sélectionner votre compte membre"})
        
        if self.lien_membre and self.email != self.lien_membre.email:
            raise ValidationError({'email': "L'email doit correspondre à votre compte membre"})
        
        try:
            validate_email(self.email)
        except ValidationError:
            raise ValidationError({'email': "Format d'email invalide"})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    # ==========================================
    # UTILITAIRES
    # ==========================================
    
    def __str__(self):
        return f"{self.nom_complet} - {self.montant}€"
    
    class Meta:
        ordering = ['-date_don']
        verbose_name = "Don"
        verbose_name_plural = "Dons"

# ==========================================
# MODÈLE ÉVÉNEMENT (formations, apostolas, expositions, activités culturelles, etc.)
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
    
    # Informations générales
    titre = models.CharField(max_length=200, verbose_name="Titre de l'événement")
    type_event = models.CharField(max_length=50, choices=TYPE_EVENEMENT, verbose_name="Type d'événement")
    description = models.TextField(verbose_name="Description")
    
    # Dates et lieu
    date_debut = models.DateTimeField(verbose_name="Date de début")
    date_fin = models.DateTimeField(blank=True, null=True, verbose_name="Date de fin")
    lieu = models.CharField(max_length=200, verbose_name="Lieu")
    
    # Images et médias
    image = models.ImageField(upload_to='evenements/', blank=True, null=True, verbose_name="Image principale")
    galerie_images = models.TextField(blank=True, null=True, help_text="URLs des images supplémentaires (séparées par des virgules)", verbose_name="Galerie d'images")
    
    # Participants et statistiques
    nombre_participants = models.IntegerField(default=0, verbose_name="Nombre de participants")
    nombre_jumeaux_present = models.IntegerField(default=0, verbose_name="Nombre de jumeaux présents")
    nombre_parents_present = models.IntegerField(default=0, verbose_name="Nombre de parents présents")
    
    # Statut et visibilité
    statut = models.CharField(max_length=20, choices=STATUT_EVENEMENT, default='a_venir', verbose_name="Statut")
    est_visible_site = models.BooleanField(default=True, verbose_name="Afficher sur le site")
    
    # Résultat / compte-rendu (après l'événement)
    compte_rendu = models.TextField(blank=True, null=True, verbose_name="Compte-rendu / Résultats")
    
    # Date de création
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    # ==========================================
    # LOGIQUE MÉTIER
    # ==========================================
    
    def clean(self):
        """Validation avant sauvegarde"""
        
        # 1. Vérifier que la date de fin est après la date de début
        if self.date_fin and self.date_fin <= self.date_debut:
            raise ValidationError({'date_fin': "La date de fin doit être postérieure à la date de début"})
        
        # 2. Vérifier que le nombre de participants est cohérent
        if self.nombre_participants < 0:
            raise ValidationError({'nombre_participants': "Le nombre de participants ne peut pas être négatif"})
    
    def save(self, *args, **kwargs):
        """Sauvegarde avec mise à jour automatique du statut"""
        
        # Mise à jour automatique du statut basé sur les dates
        if self.date_debut > timezone.now():
            self.statut = 'a_venir'
        elif self.date_debut <= timezone.now() and (not self.date_fin or self.date_fin >= timezone.now()):
            self.statut = 'en_cours'
        elif self.date_fin and self.date_fin < timezone.now():
            self.statut = 'termine'
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def est_passe(self):
        """Vrai si l'événement est terminé"""
        if self.date_fin:
            return self.date_fin < timezone.now()
        return self.date_debut < timezone.now()
    
    def duree_en_heures(self):
        """Calcule la durée de l'événement en heures"""
        if self.date_fin:
            delta = self.date_fin - self.date_debut
            return round(delta.total_seconds() / 3600, 1)
        return None
    
    def total_participants(self):
        """Retourne le nombre total de participants (jumeaux + parents)"""
        return self.nombre_jumeaux_present + self.nombre_parents_present
    
    def get_galerie_list(self):
        """Retourne la liste des URLs des images de la galerie"""
        if self.galerie_images:
            return [url.strip() for url in self.galerie_images.split(',') if url.strip()]
        return []
    
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
    
    # Informations principales
    titre = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL personnalisée")
    contenu = models.TextField(verbose_name="Contenu")
    extrait = models.TextField(blank=True, null=True, max_length=300, verbose_name="Extrait (résumé)")
    categorie = models.CharField(max_length=50, choices=CATEGORIE_ACTUALITE, default='annonce', verbose_name="Catégorie")
    
    # Images
    image_principale = models.ImageField(upload_to='actualites/', blank=True, null=True, verbose_name="Image principale")
    
    # Visibilité
    est_publie = models.BooleanField(default=True, verbose_name="Publié ?")
    date_publication = models.DateTimeField(auto_now_add=True, verbose_name="Date de publication")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    # Pour les actualités liées à un événement
    evenement_lie = models.ForeignKey(
        'Evenement', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Événement lié"
    )
    
    # ==========================================
    # LOGIQUE MÉTIER
    # ==========================================
    
    def save(self, *args, **kwargs):
        """Génération automatique du slug si non fourni"""
        if not self.slug:
            import re
            self.slug = re.sub(r'[^a-z0-9]+', '-', self.titre.lower()).strip('-')
        super().save(*args, **kwargs)
    
    def get_extrait(self):
        """Retourne l'extrait ou les 150 premiers caractères du contenu"""
        if self.extrait:
            return self.extrait
        if len(self.contenu) > 150:
            return self.contenu[:150] + "..."
        return self.contenu
    
    def est_recent(self):
        """Vrai si l'actualité date de moins de 7 jours"""
        return self.date_publication >= (timezone.now() - timedelta(days=7))
    
    def __str__(self):
        return self.titre
    
    class Meta:
        ordering = ['-date_publication']
        verbose_name = "Actualité"
        verbose_name_plural = "Actualités"
        
# ==========================================
# MODÈLE COTISATION (membres uniquement)
# ==========================================

class Cotisation(models.Model):
    STATUT_CHOICES = [
        ('paye', 'Payé'),
        ('en_attente', 'En attente'),
        ('en_retard', 'En retard'),
        ('exonere', 'Exonéré'),
    ]
    
    PERIODE_CHOICES = [
        ('mensuelle', 'Mensuelle'),
        ('trimestrielle', 'Trimestrielle'),
        ('semestrielle', 'Semestrielle'),
        ('annuelle', 'Annuelle'),
    ]
    
    # Lien vers le membre (obligatoire)
    membre = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name="Membre")
    
    # Informations sur la cotisation
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant (€)")
    periode = models.CharField(max_length=20, choices=PERIODE_CHOICES, default='annuelle', verbose_name="Périodicité")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    
    # Dates
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin", blank=True, null=True)
    date_paiement = models.DateTimeField(blank=True, null=True, verbose_name="Date de paiement")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    # Méthode de paiement et référence
    methode_paiement = models.CharField(max_length=50, blank=True, null=True, verbose_name="Méthode de paiement")
    reference_paiement = models.CharField(max_length=100, blank=True, null=True, verbose_name="Référence")
    commentaire = models.TextField(blank=True, null=True, verbose_name="Commentaire")
    
    # ==========================================
    # LOGIQUE MÉTIER
    # ==========================================
    
    def clean(self):
        """Validation avant sauvegarde"""
        if self.montant <= 0:
            raise ValidationError({'montant': "Le montant doit être supérieur à 0€"})
        
        if self.date_debut and self.date_fin and self.date_fin <= self.date_debut:
            raise ValidationError({'date_fin': "La date de fin doit être postérieure à la date de début"})
        
        if self.statut == 'paye' and not self.date_paiement:
            from django.utils import timezone
            self.date_paiement = timezone.now()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def est_actif(self):
        """Vrai si la cotisation est encore valide"""
        if self.statut == 'paye' and self.date_fin:
            return self.date_fin >= timezone.now().date()
        return False
    
    def est_en_retard(self):
        """Vrai si la cotisation est en retard"""
        if self.statut != 'paye' and self.date_fin and self.date_fin < timezone.now().date():
            return True
        return False
    
    def __str__(self):
        return f"{self.membre.nom_complet} - {self.montant}€ - {self.statut}"
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Cotisation"
        verbose_name_plural = "Cotisations"