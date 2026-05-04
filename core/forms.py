from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Cotisation, Evenement


class UserForm(UserCreationForm):
    type_roles = forms.MultipleChoiceField(
        choices=User.ROLES,
        widget=forms.CheckboxSelectMultiple,
        label="Vous êtes",
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'nom_complet', 'telephone', 'adresse', 'pays', 'ville',
            'noms_jumeaux_lies', 'nom_papa', 'nom_maman', 'etat_civil', 
            'statut_pro', 'photo', 'type_roles'
        ]
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 3}),
            'noms_jumeaux_lies': forms.Textarea(attrs={'rows': 2}),
            'photo': forms.FileInput(attrs={'accept': 'image/jpeg,image/png'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['noms_jumeaux_lies'].required = False
        self.fields['nom_papa'].required = False
        self.fields['nom_maman'].required = False
        self.fields['etat_civil'].required = False
        self.fields['statut_pro'].required = False
        self.fields['ville'].required = False
        self.fields['photo'].required = False
        
        for field in self.fields:
            if not isinstance(self.fields[field].widget, forms.CheckboxSelectMultiple):
                self.fields[field].widget.attrs.update({'class': 'w-full border rounded px-3 py-2'})
        
        self.fields['password1'].widget.attrs.update({'class': 'w-full border rounded px-3 py-2'})
        self.fields['password2'].widget.attrs.update({'class': 'w-full border rounded px-3 py-2'})


class SoumissionCotisationForm(forms.ModelForm):
    class Meta:
        model = Cotisation
        fields = ['type_cotisation', 'mois', 'evenement', 'montant', 'justificatif']
        widgets = {
            'mois': forms.DateInput(attrs={'type': 'month', 'class': 'w-full border rounded px-3 py-2'}),
            'justificatif': forms.FileInput(attrs={'class': 'w-full border rounded px-3 py-2', 'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['evenement'].queryset = Evenement.objects.filter(statut='a_venir')
        self.fields['evenement'].required = False
        self.fields['mois'].required = False
        self.fields['montant'].widget.attrs.update({'placeholder': 'Ex: 10.00'})