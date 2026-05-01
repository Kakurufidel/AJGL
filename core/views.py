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
            user = form.save(commit=False)
            roles = ','.join(form.cleaned_data['type_roles'])
            user.type_roles = roles
            user.set_password(form.cleaned_data['password1'])
            user.save()
            # Connexion automatique après inscription
            from django.contrib.auth import login
            login(request, user)
            messages.success(request, "Inscription réussie ! Bienvenue !")
            return redirect('accueil')
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