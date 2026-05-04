from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .forms import UserForm, SoumissionCotisationForm
from .models import Cotisation
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_protect





# ==========================================
# PAGE D'ACCUEIL
# ==========================================

class AccueilView(View):
    def get(self, request):
        return render(request, 'core/accueil.html')


# ==========================================
# PAGE À PROPOS
# ==========================================

class AProposView(View):
    def get(self, request):
        return render(request, 'core/a-propos.html')




# ==========================================
# CONNEXION / DÉCONNEXION
# ==========================================

class ConnexionView(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return '/tableau-de-bord/'

@method_decorator(csrf_protect, name='dispatch')
class DeconnexionView(View):
    def post(self, request):
        logout(request)
        return redirect('accueil')

# ==========================================
# TABLEAU DE BORD (pour les éditeurs)
# ==========================================

@method_decorator(login_required, name='dispatch')
class TableauBordView(View):
    def get(self, request):
        return render(request, 'core/tableau-bord.html')

# ==========================================
# PAGE NOS ACTIONS
# ==========================================

class NosActionsView(View):
    def get(self, request):
        return render(request, 'core/nos-actions.html')


# ==========================================
# PAGE RÉALISATIONS
# ==========================================

class RealisationsView(View):
    def get(self, request):
        return render(request, 'core/realisations.html')


# ==========================================
# PAGE ADHÉSION (formulaire)
# ==========================================

class AdhesionView(View):
    def get(self, request):
        form = UserForm()
        return render(request, 'core/adhesion.html', {'form': form})
    
    def post(self, request):
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                # Récupérer les rôles cochés
                roles = request.POST.getlist('type_roles')
                user.type_roles = ','.join(roles)
                
                # Sauvegarder l'utilisateur dans la BD
                user.set_password(form.cleaned_data['password1'])
                user.save()
                
                # Connecter l'utilisateur automatiquement
                login(request, user)
                
                # Message de succès
                messages.success(request, "✅ Inscription réussie ! Bienvenue à l'AJ-GL Asbl !")
                return redirect('accueil')
                
            except Exception as e:
                messages.error(request, f"❌ Erreur lors de l'inscription : {str(e)}")
                return render(request, 'core/adhesion.html', {'form': form})
        else:
            # Afficher les erreurs du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {field}: {error}")
            return render(request, 'core/adhesion.html', {'form': form})# ==========================================
# PAGE DON (formulaire)
# ==========================================

# class DonView(View):
#     def get(self, request):
#         form = DonForm()
#         return render(request, 'core/don.html', {'form': form})
    
#     def post(self, request):
#         form = DonForm(request.POST)
#         if form.is_valid():
#             don = form.save()
#             messages.success(request, f"Merci pour votre don de {don.montant}€ !")
#             return redirect('don')
#         return render(request, 'core/don.html', {'form': form})


# ==========================================
# PAGE CONTACT
# ==========================================

class ContactView(View):
    def get(self, request):
        return render(request, 'core/contact.html')
    

@method_decorator(login_required, name='dispatch')
class SoumettreCotisationView(View):
    def get(self, request):
        form = SoumissionCotisationForm()
        return render(request, 'core/soumettre_cotisation.html', {'form': form})
    
    def post(self, request):
        form = SoumissionCotisationForm(request.POST, request.FILES)
        if form.is_valid():
            cotisation = form.save(commit=False)
            cotisation.membre = request.user
            cotisation.statut = 'en_attente'
            cotisation.save()
            
            # Notification aux coordinateurs (à implémenter)
            messages.success(request, "Votre cotisation a été envoyée pour validation.")
            return redirect('mes_cotisations')
        return render(request, 'core/soumettre_cotisation.html', {'form': form})
    
@method_decorator(login_required, name='dispatch')
class MesCotisationsView(View):
    def get(self, request):
        cotisations = Cotisation.objects.filter(membre=request.user)
        return render(request, 'core/mes_cotisations.html', {'cotisations': cotisations})

@method_decorator(login_required, name='dispatch')
class MonProfilView(View):
    def get(self, request):
        return render(request, 'core/profil.html', {'user': request.user})
    
    def post(self, request):
        # Mise à jour du profil
        user = request.user
        user.nom_complet = request.POST.get('nom_complet')
        user.telephone = request.POST.get('telephone')
        user.adresse = request.POST.get('adresse')
        user.ville = request.POST.get('ville')
        user.save()
        messages.success(request, "Profil mis à jour !")
        return redirect('profil')