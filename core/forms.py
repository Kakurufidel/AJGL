from django import forms
from .models import User, Don

# ==========================================
# FORMULAIRE D'ADHÉSION (INSCRIPTION MEMBRE)
# ==========================================

class UserForm(forms.ModelForm):
    # Champs supplémentaires pour les rôles (checkbox multiples)
    type_roles = forms.MultipleChoiceField(
        choices=User.ROLES,
        widget=forms.CheckboxSelectMultiple,
        label="Vous êtes",
        help_text="Vous pouvez choisir plusieurs options (ex: parent ET jumeau)"
    )
    
    class Meta:
        model = User
        fields = [
            'nom_complet',
            'noms_jumeaux_lies',
            'nom_papa',
            'nom_maman',
            'adresse',
            'pays',
            'ville',
            'etat_civil',
            'statut_pro',
            'telephone',
            'email',
            'photo',
        ]
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Commune, Quartier, Avenue'}),
            'noms_jumeaux_lies': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Séparez les noms par des virgules'}),
            'photo': forms.FileInput(attrs={'accept': 'image/jpeg,image/png'}),
        }
        labels = {
            'nom_complet': 'Nom complet',
            'noms_jumeaux_lies': 'Noms des jumeaux/triplés',
            'nom_papa': 'Nom du père',
            'nom_maman': 'Nom de la mère',
            'adresse': 'Adresse',
            'pays': 'Pays',
            'ville': 'Ville',
            'etat_civil': 'État civil',
            'statut_pro': 'Statut professionnel',
            'telephone': 'Téléphone',
            'email': 'Email',
            'photo': 'Photo (optionnel)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre certains champs optionnels
        self.fields['noms_jumeaux_lies'].required = False
        self.fields['nom_papa'].required = False
        self.fields['nom_maman'].required = False
        self.fields['etat_civil'].required = False
        self.fields['statut_pro'].required = False
        self.fields['ville'].required = False
        self.fields['photo'].required = False
        
        # Ajouter des classes CSS pour Tailwind
        for field in self.fields:
            if not isinstance(self.fields[field].widget, forms.CheckboxSelectMultiple):
                self.fields[field].widget.attrs.update({'class': 'w-full border rounded px-3 py-2'})


# ==========================================
# FORMULAIRE DE DON
# ==========================================

class DonForm(forms.ModelForm):
    class Meta:
        model = Don
        fields = [
            'nom_complet',
            'email',
            'telephone',
            'est_membre',
            'lien_membre',
            'montant',
            'methode_paiement',
            'message',
        ]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Un message d’encouragement ? (optionnel)'}),
            'lien_membre': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2'}),
        }
        labels = {
            'nom_complet': 'Votre nom complet',
            'email': 'Votre email',
            'telephone': 'Votre téléphone',
            'est_membre': 'Je suis déjà membre de l’association',
            'lien_membre': 'Sélectionnez votre compte membre',
            'montant': 'Montant du don (€)',
            'methode_paiement': 'Moyen de paiement',
            'message': 'Message (optionnel)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Champs optionnels
        self.fields['message'].required = False
        self.fields['lien_membre'].required = False
        
        # Ajouter des classes CSS pour Tailwind
        for field in self.fields:
            if not isinstance(self.fields[field].widget, forms.CheckboxInput):
                if not isinstance(self.fields[field].widget, forms.Select):
                    self.fields[field].widget.attrs.update({'class': 'w-full border rounded px-3 py-2'})
        
        # Le champ est_membre a une classe spéciale
        self.fields['est_membre'].widget.attrs.update({'class': 'mr-2'})
        
# ==========================================
# FORMULAIRE DE COTISATION
# ==========================================

class CotisationForm(forms.ModelForm):
    class Meta:
        model = Cotisation
        fields = [
            'membre',
            'montant',
            'periode',
            'statut',
            'date_debut',
            'date_fin',
            'methode_paiement',
            'reference_paiement',
            'commentaire',
        ]
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded px-3 py-2'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded px-3 py-2'}),
            'commentaire': forms.Textarea(attrs={'rows': 3, 'class': 'w-full border rounded px-3 py-2'}),
            'membre': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if not isinstance(self.fields[field].widget, forms.DateInput):
                if not isinstance(self.fields[field].widget, forms.Select):
                    if not hasattr(self.fields[field].widget, 'attrs'):
                        self.fields[field].widget.attrs.update({'class': 'w-full border rounded px-3 py-2'})