from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Cotisation, Contribution, Evenement, Cellule


# ==========================================
# FORMULAIRE D'INSCRIPTION (ADHÉSION)
# ==========================================
class UserForm(UserCreationForm):
    type_roles = forms.MultipleChoiceField(
        choices=[
            ('parent', 'Parent'),
            ('jumeau', 'Jumeau'),
            ('jumelle', 'Jumelle'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Vous êtes"
    )

    nom_jumeau_lie = forms.CharField(
        max_length=100,
        required=False,
        label="Nom de mon jumeau / ma jumelle"
    )

    noms_enfants_jumeaux = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        label="Noms de mes enfants jumeaux"
    )

    genre = forms.ChoiceField(
        choices=User.SEXE_CHOICES,
        required=False,
        label="Genre"
    )

    date_naissance = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date de naissance"
    )

    class Meta:
        model = User
        fields = [
            'email', 'nom_complet', 'telephone',
            'pays', 'ville', 'adresse', 'photo',
            'type_roles', 'nom_jumeau_lie', 'noms_enfants_jumeaux',
            'genre', 'date_naissance'
        ]
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 2}),
            'photo': forms.FileInput(attrs={'accept': 'image/jpeg,image/png'}),
        }
        error_messages = {
            'email': {
                'unique': "Cet email est déjà utilisé par un autre membre.",
                'invalid': "Veuillez entrer une adresse email valide.",
            },
            'nom_complet': {
                'required': "Le nom complet est obligatoire.",
            },
            'telephone': {
                'required': "Le numéro de téléphone est obligatoire.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if not isinstance(self.fields[field].widget, forms.CheckboxSelectMultiple):
                self.fields[field].widget.attrs.update({'class': 'w-full border rounded px-3 py-2'})
        self.fields['noms_enfants_jumeaux'].widget.attrs.update({'rows': 2, 'class': 'w-full border rounded px-3 py-2'})
        self.fields['photo'].widget.attrs.update({'class': 'w-full'})

        # Messages d'erreur pour les mots de passe
        self.fields['password1'].error_messages = {'required': "Veuillez entrer un mot de passe."}
        self.fields['password2'].error_messages = {'required': "Veuillez confirmer votre mot de passe."}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé. Connectez-vous ou utilisez un autre email.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")
        return password2

# ==========================================
# FORMULAIRE DE CONNEXION (EMAIL)
# ==========================================

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full border rounded px-3 py-2',
        'placeholder': 'votre@email.com'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full border rounded px-3 py-2',
        'placeholder': 'Votre mot de passe'
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Email"


# ==========================================
# FORMULAIRE PROFIL (MODIFICATION)
# ==========================================

class ProfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nom_complet', 'telephone', 'pays', 'ville', 'adresse', 'photo']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'w-full border rounded px-3 py-2'})


# ==========================================
# FORMULAIRE COTISATION (CREATION PAR ADMIN/COORDINATEUR)
# ==========================================

class CotisationForm(forms.ModelForm):
    class Meta:
        model = Cotisation
        fields = [
            'titre', 'description', 'type', 'obligatoire',
            'numero_paiement', 'nom_beneficiaire',
            'date_debut', 'date_fin', 'evenement'
        ]
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded px-3 py-2'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded px-3 py-2'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['evenement'].queryset = Evenement.objects.filter(statut='a_venir')
        self.fields['evenement'].required = False
        self.fields['description'].required = False

        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'w-full border rounded px-3 py-2'})


# ==========================================
# FORMULAIRE DE SOUMISSION DE CONTRIBUTION (PAR MEMBRE)
# ==========================================

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['cotisation', 'montant', 'preuve_paiement']
        widgets = {
            'preuve_paiement': forms.FileInput(attrs={'accept': 'image/jpeg,image/png'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrer les cotisations actives
        from django.utils import timezone
        self.fields['cotisation'].queryset = Cotisation.objects.filter(
            statut='valide',
            date_debut__lte=timezone.now().date(),
            date_fin__gte=timezone.now().date()
        )
        self.fields['cotisation'].label = "Sélectionnez la cotisation"
        self.fields['montant'].widget.attrs.update({'class': 'w-full border rounded px-3 py-2'})
        self.fields['montant'].help_text = "Montant en euros (€)"

    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant and montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à 0")
        return montant


# ==========================================
# FORMULAIRE DE VALIDATION DE CONTRIBUTION (PAR COORDINATEUR)
# ==========================================

class ValidationContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['statut', 'commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['statut'].widget.attrs.update({'class': 'w-full border rounded px-3 py-2'})
        self.fields['commentaire'].widget.attrs.update({'class': 'w-full border rounded px-3 py-2'})
        self.fields['commentaire'].required = False
        self.fields['commentaire'].help_text = "Optionnel, surtout pour expliquer un rejet"


# ==========================================
# FORMULAIRE DE CONTACT (SITE PUBLIC)
# ==========================================

class ContactForm(forms.Form):
    nom = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'w-full border rounded px-3 py-2',
        'placeholder': 'Votre nom complet'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full border rounded px-3 py-2',
        'placeholder': 'votre@email.com'
    }))
    telephone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full border rounded px-3 py-2',
        'placeholder': 'Optionnel'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'w-full border rounded px-3 py-2',
        'rows': 4,
        'placeholder': 'Votre message...'
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'telephone':
                self.fields[field].required = True
                
class CelluleForm(forms.ModelForm):
    class Meta:
        model = Cellule
        fields = ['nom', 'quartier', 'ville', 'pays', 'responsable', 'telephone', 'email', 'description', 'est_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'w-full border rounded-lg px-4 py-2'})
        self.fields['est_active'].widget.attrs.update({'class': 'w-4 h-4'})