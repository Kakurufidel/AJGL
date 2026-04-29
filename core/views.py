from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .forms import UserForm, DonForm
from .models import User, Don
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect

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

class DeconnexionView(LogoutView):
    next_page = 'accueil'

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
            # Récupérer les rôles cochés
            roles = form.cleaned_data.get('type_roles')
            # Sauvegarder l'utilisateur
            user = form.save(commit=False)
            user.type_roles = ','.join(roles)  # "parent,jumeau" ou "parent" ou "jumeau"
            user.save()
            messages.success(request, "Votre inscription a bien été enregistrée !")
            return redirect('adhesion')
        return render(request, 'core/adhesion.html', {'form': form})


# ==========================================
# PAGE DON (formulaire)
# ==========================================

class DonView(View):
    def get(self, request):
        form = DonForm()
        return render(request, 'core/don.html', {'form': form})
    
    def post(self, request):
        form = DonForm(request.POST)
        if form.is_valid():
            don = form.save()
            messages.success(request, f"Merci pour votre don de {don.montant}€ !")
            return redirect('don')
        return render(request, 'core/don.html', {'form': form})


# ==========================================
# PAGE CONTACT
# ==========================================

class ContactView(View):
    def get(self, request):
        return render(request, 'core/contact.html')