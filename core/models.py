from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils import timezone


# ==========================================
# USER MANAGER
# ==========================================

class CustomUserManager(BaseUserManager):
    def create_user(self, email, nom_complet, telephone, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            nom_complet=nom_complet,
            telephone=telephone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom_complet, telephone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, nom_complet, telephone, password, **extra_fields)


# ==========================================
# USER (MEMBER)
# ==========================================

class User(AbstractUser):
    username = None  # Désactiver le champ username
    email = models.EmailField(unique=True, db_index=True)

    # Informations personnelles
    nom_complet = models.CharField(max_length=100, verbose_name="Nom complet")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone")
    photo = models.ImageField(upload_to='photos/', blank=True, null=True, verbose_name="Photo de profil")

    # Localisation
    pays = models.CharField(max_length=50, blank=True, null=True, verbose_name="Pays")
    ville = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ville")
    adresse = models.TextField(blank=True, null=True, verbose_name="Adresse complète")

    # Configuration Django
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom_complet', 'telephone']

    objects = CustomUserManager()

    def __str__(self):
        return self.nom_complet

    # ===== Helpers pour les permissions =====
    def is_admin(self):
        return self.is_superuser

    def is_editor(self):
        return self.is_staff and not self.is_superuser

    def is_member(self):
        return self.is_authenticated

    class Meta:
        verbose_name = "Membre"
        verbose_name_plural = "Membres"


# ==========================================
# EVENEMENT (EVENT)
# ==========================================

class Evenement(models.Model):
    class StatutChoices(models.TextChoices):
        A_VENIR = 'a_venir', 'À venir'
        EN_COURS = 'en_cours', 'En cours'
        TERMINE = 'termine', 'Terminé'
        ANNULE = 'annule', 'Annulé'

    titre = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")

    date_debut = models.DateTimeField(db_index=True, verbose_name="Date de début")
    date_fin = models.DateTimeField(blank=True, null=True, verbose_name="Date de fin")

    lieu = models.CharField(max_length=200, verbose_name="Lieu")

    statut = models.CharField(
        max_length=20,
        choices=StatutChoices.choices,
        default=StatutChoices.A_VENIR,
        db_index=True
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    # Image principale
    image = models.ImageField(upload_to='evenements/', blank=True, null=True, verbose_name="Image")

    def save(self, *args, **kwargs):
        now = timezone.now()

        if self.date_debut > now:
            self.statut = self.StatutChoices.A_VENIR
        elif self.date_fin and self.date_fin < now:
            self.statut = self.StatutChoices.TERMINE
        elif self.date_debut <= now <= (self.date_fin or now):
            self.statut = self.StatutChoices.EN_COURS
        else:
            self.statut = self.StatutChoices.A_VENIR

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titre} - {self.date_debut.strftime('%d/%m/%Y')}"

    class Meta:
        ordering = ['-date_debut']
        verbose_name = "Événement"
        verbose_name_plural = "Événements"


# ==========================================
# COTISATION (WHAT NEEDS TO BE PAID)
# ==========================================

class Cotisation(models.Model):
    class TypeChoices(models.TextChoices):
        MENSUELLE = 'mensuelle', 'Mensuelle'
        SPECIALE = 'speciale', 'Spéciale'

    class StatutChoices(models.TextChoices):
        BROUILLON = 'brouillon', 'Brouillon'
        VALIDE = 'valide', 'Validée'

    titre = models.CharField(max_length=200, verbose_name="Titre de la cotisation")
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    evenement = models.ForeignKey(
        Evenement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cotisations",
        verbose_name="Événement lié (optionnel)"
    )

    type = models.CharField(max_length=20, choices=TypeChoices.choices, verbose_name="Type")
    obligatoire = models.BooleanField(default=False, verbose_name="Cotisation obligatoire")

    # Informations bancaires
    numero_paiement = models.CharField(
        max_length=100,
        verbose_name="Numéro de compte / RIB",
        db_index=True
    )
    nom_beneficiaire = models.CharField(
        max_length=200,
        verbose_name="Intitulé du compte / Nom du bénéficiaire"
    )

    # Validation
    cree_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="cotisations_creees",
        verbose_name="Créée par"
    )
    valide_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cotisations_validees",
        verbose_name="Validée par"
    )
    statut = models.CharField(
        max_length=20,
        choices=StatutChoices.choices,
        default=StatutChoices.BROUILLON,
        db_index=True,
        verbose_name="Statut"
    )

    # Période de validité
    date_debut = models.DateField(db_index=True, verbose_name="Date de début")
    date_fin = models.DateField(db_index=True, verbose_name="Date de fin")

    date_validation = models.DateTimeField(null=True, blank=True, verbose_name="Date de validation")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        permissions = [
            ("can_validate_cotisation", "Peut valider une cotisation"),
        ]
        indexes = [
            models.Index(fields=['statut', 'date_debut']),
        ]
        verbose_name = "Cotisation"
        verbose_name_plural = "Cotisations"

    def clean(self):
        if self.date_fin <= self.date_debut:
            raise ValidationError("La date de fin doit être après la date de début")

        if self.date_debut < timezone.now().date() and self.statut == self.StatutChoices.BROUILLON:
            raise ValidationError("Une cotisation en brouillon ne peut pas commencer dans le passé")

    def valider(self, admin_user):
        self.statut = self.StatutChoices.VALIDE
        self.valide_par = admin_user
        self.date_validation = timezone.now()
        self.save()

    def est_active(self):
        today = timezone.now().date()
        return self.statut == self.StatutChoices.VALIDE and self.date_debut <= today <= self.date_fin

    def __str__(self):
        return f"{self.titre} ({self.get_type_display()})"


# ==========================================
# CONTRIBUTION (ACTUAL PAYMENT)
# ==========================================

class Contribution(models.Model):
    class StatutChoices(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        VALIDE = 'valide', 'Validée'
        REJETEE = 'rejetee', 'Rejetée'

    membre = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="contributions",
        verbose_name="Membre"
    )
    cotisation = models.ForeignKey(
        Cotisation,
        on_delete=models.CASCADE,
        related_name="contributions",
        verbose_name="Cotisation concernée"
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant payé (€)")
    preuve_paiement = models.ImageField(upload_to='preuves/', verbose_name="Preuve de paiement")

    statut = models.CharField(
        max_length=20,
        choices=StatutChoices.choices,
        default=StatutChoices.EN_ATTENTE,
        db_index=True,
        verbose_name="Statut"
    )
    commentaire = models.TextField(blank=True, null=True, verbose_name="Commentaire (rejet, etc.)")

    valide_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contributions_validees",
        verbose_name="Validée par"
    )
    date_validation = models.DateTimeField(null=True, blank=True, verbose_name="Date de validation")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de soumission")

    class Meta:
        permissions = [
            ("can_validate_contribution", "Peut valider une contribution"),
        ]
        unique_together = ['membre', 'cotisation']
        indexes = [
            models.Index(fields=['statut']),
            models.Index(fields=['cotisation', 'statut']),
        ]
        verbose_name = "Contribution"
        verbose_name_plural = "Contributions"

    def clean(self):
        if self.montant <= 0:
            raise ValidationError("Le montant doit être supérieur à 0")

        if not self.preuve_paiement:
            raise ValidationError("La preuve de paiement est obligatoire")

        if not self.cotisation.est_active():
            raise ValidationError("Cette cotisation n'est plus active")

    def valider(self, admin_user):
        self.statut = self.StatutChoices.VALIDE
        self.valide_par = admin_user
        self.date_validation = timezone.now()
        self.save()

    def rejeter(self, raison):
        self.statut = self.StatutChoices.REJETEE
        self.commentaire = raison
        self.save()

    def __str__(self):
        return f"{self.membre.nom_complet} - {self.montant}€ - {self.cotisation.titre}"