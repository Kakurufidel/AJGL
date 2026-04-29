from django.db import models
from django.core.exceptions import ValidationError

# ==========================================
# MODÈLE USER (MEMBRE)
# ==========================================

class User(models.Model):
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
    email = models.EmailField(unique=True)
    
    # Champs pour les jumeaux
    noms_jumeaux_lies = models.TextField(blank=True, null=True, help_text="Noms des jumeaux/triplés (séparés par des virgules)")
    
    # Champs pour les parents
    nom_papa = models.CharField(max_length=100, blank=True, null=True)
    nom_maman = models.CharField(max_length=100, blank=True, null=True)
    etat_civil = models.CharField(max_length=20, choices=ETAT_CIVIL, blank=True, null=True)
    statut_pro = models.CharField(max_length=20, choices=STATUT_PRO, blank=True, null=True)
    
    # Photo et rôles
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    type_roles = models.CharField(max_length=50, help_text="parent,jumeau ou parent ou jumeau")
    
    # Date d'inscription
    date_inscription = models.DateTimeField(auto_now_add=True)
    
    # ==========================================
    # VALIDATIONS
    # ==========================================
    
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
    
    # ==========================================
    # UTILITAIRES
    # ==========================================
    
    def __str__(self):
        return f"{self.nom_complet} ({self.get_pays_display()})"
    
    def get_roles_list(self):
        return self.type_roles.split(',')
    
    class Meta:
        ordering = ['-date_inscription']
        verbose_name = "Membre"
        verbose_name_plural = "Membres"
        unique_together = ['nom_complet', 'email']


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