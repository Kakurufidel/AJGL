from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Evenement, Actualite, Cotisation, User
from django.contrib.auth.mixins import UserPassesTestMixin

# ==========================================
# CRÉATION DES GROUPES ET PERMISSIONS
# ==========================================

def creer_groupes_et_permissions():

    editeur_group, _ = Group.objects.get_or_create(name='Editeur')
    permissions_editeur = [
        'add_evenement', 'change_evenement', 'view_evenement',
        'add_actualite', 'change_actualite', 'view_actualite',
        'view_cotisation',
    ]
    for perm in permissions_editeur:
        try:
            editeur_group.permissions.add(Permission.objects.get(codename=perm))
        except Permission.DoesNotExist:
            pass
    
    # 2. Groupe COORDONNATEUR
    coordo_group, _ = Group.objects.get_or_create(name='Coordinateur')
    permissions_coordo = [
        'add_evenement', 'change_evenement', 'delete_evenement', 'view_evenement',
        'add_actualite', 'change_actualite', 'delete_actualite', 'view_actualite',
        'add_cotisation', 'change_cotisation', 'view_cotisation',
        'add_user', 'change_user', 'view_user',
    ]
    for perm in permissions_coordo:
        try:
            coordo_group.permissions.add(Permission.objects.get(codename=perm))
        except Permission.DoesNotExist:
            pass
    
    print("Groupes et permissions créés avec succès !")


# ==========================================
# VÉRIFICATION DES PERMISSIONS DANS LES VUES
# ==========================================

class EditeurRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_superuser or
            self.request.user.groups.filter(name='Editeur').exists() or
            self.request.user.groups.filter(name='Coordinateur').exists()
        )

class CoordinateurRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_superuser or
            self.request.user.groups.filter(name='Coordinateur').exists()
        )