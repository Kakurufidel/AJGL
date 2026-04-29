from django.db import models

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
    
    # Champs principaux obligatoires
    nom_complet = models.CharField(max_length=100)
    adresse = models.TextField()
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
    
    def __str__(self):
        return self.nom_complet
    
    def get_roles_list(self):
        """Retourne la liste des rôles (ex: ['parent', 'jumeau'])"""
        return self.type_roles.split(',')
    
    class Meta:
        ordering = ['-date_inscription']
        verbose_name = "Membre"
        verbose_name_plural = "Membres"