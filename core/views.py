from django.shortcuts import render, redirect
from django.views import View
from datetime import date
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.db.models import Sum
from django.utils import timezone
from .forms import (
    UserForm, EmailAuthenticationForm, ProfilForm,
    CotisationForm, ContributionForm, ValidationContributionForm,CelluleForm
)
from .models import *


# ==========================================
# PAGES PUBLIQUES
# ==========================================

class AccueilView(View):
    def get(self, request):
        context = {
            # 'actualites': Actualite.objects.filter(est_publie=True).order_by('-date_publication')[:3],
            'evenements_a_venir': Evenement.objects.filter(
                statut='a_venir',
                date_debut__gte=timezone.now()
            ).order_by('date_debut')[:3],
        }
        return render(request, 'core/home.html', context)


class AProposView(View):
    def get(self, request):
        return render(request, 'core/about.html')


class NosActionsView(View):
    def get(self, request):
        return render(request, 'core/actions.html')


class RealisationsView(View):
    def get(self, request):
        return render(request, 'core/achievements.html')


class ContactView(View):
    def get(self, request):
        return render(request, 'core/contact.html')


# ==========================================
# AUTHENTIFICATION
# ==========================================

from django.contrib.auth.views import LoginView

class ConnexionView(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True
    form_class = EmailAuthenticationForm

    def get_success_url(self):
        # Redirige vers la page que l'utilisateur visitait avant la connexion
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return '/'  # Sinon, retour à l'accueil
@method_decorator(csrf_protect, name='dispatch')
class DeconnexionView(View):
    def post(self, request):
        logout(request)
        return redirect('home')


# ==========================================
# INSCRIPTION & PROFIL
# ==========================================

class AdhesionView(View):
    def get(self, request):
        form = UserForm()
        return render(request, 'core/register.html', {'form': form})

    def post(self, request):
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])

            # Rôles
            roles = request.POST.getlist('type_roles')
            user.type_roles = ','.join(roles) if roles else ''

            # Champs supplémentaires
            user.nom_jumeau_lie = form.cleaned_data.get('nom_jumeau_lie', '')
            user.noms_enfants_jumeaux = form.cleaned_data.get('noms_enfants_jumeaux', '')
            user.genre = form.cleaned_data.get('genre', '')
            user.date_naissance = form.cleaned_data.get('date_naissance', None)

            user.save()
            login(request, user)
            messages.success(request, "Inscription réussie ! Bienvenue !")
            return redirect('home')
        return render(request, 'core/register.html', {'form': form})
    
@method_decorator(login_required, name='dispatch')
class MonProfilView(View):
    def get(self, request):
        form = ProfilForm(instance=request.user)
        return render(request, 'core/profile.html', {'form': form})

    def post(self, request):
        form = ProfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour !")
            return redirect('profile')
        return render(request, 'core/profile.html', {'form': form})


# ==========================================
# DASHBOARD UNIQUE (MEMBRE + STAFF)
# ==========================================

@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
        user = request.user

        # Données pour le membre
        contributions = Contribution.objects.filter(membre=user).select_related('cotisation').order_by('-date_creation')
        total_paiements = contributions.count()
        paiements_valides = contributions.filter(statut='valide').count()
        paiements_attente = contributions.filter(statut='en_attente').count()

        context = {
            'contributions': contributions[:5],
            'total_paiements': total_paiements,
            'paiements_valides': paiements_valides,
            'paiements_attente': paiements_attente,
        }

        # Données pour le staff
        if user.is_staff or user.is_superuser:
            membres = User.objects.filter(is_active=True)
            today = date.today()

            # Calcul de l'âge moyen et répartition
            ages = []
            moins_de_18 = 0
            for m in membres:
                if m.date_naissance:
                    age = today.year - m.date_naissance.year - ((today.month, today.day) < (m.date_naissance.month, m.date_naissance.day))
                    ages.append(age)
                    if age < 18:
                        moins_de_18 += 1
            age_moyen = round(sum(ages) / len(ages), 1) if ages else 0

            context.update({
                'total_membres': membres.count(),
                'total_hommes': membres.filter(genre='M').count(),
                'total_femmes': membres.filter(genre='F').count(),
                'age_moyen': age_moyen,
                'moins_de_18': moins_de_18,
                'contributions_attente': Contribution.objects.filter(statut='en_attente').count(),
                'contributions_validees': Contribution.objects.filter(statut='valide').count(),
                'total_montant': Contribution.objects.filter(statut='valide').aggregate(Sum('montant'))['montant__sum'] or 0,
                'dernieres_contributions': Contribution.objects.filter(statut='en_attente').select_related('membre', 'cotisation').order_by('-date_creation')[:10],
            })

        return render(request, 'core/dashboard.html', context)
# ==========================================
# CONTRIBUTIONS (PAIEMENTS)
# ==========================================

@method_decorator(login_required, name='dispatch')
class MesContributionsView(View):
    def get(self, request):
        contributions = Contribution.objects.filter(membre=request.user).select_related('cotisation').order_by('-date_creation')
        return render(request, 'core/my_payments.html', {'contributions': contributions})

@method_decorator(login_required, name='dispatch')
class SoumettreContributionView(View):
    def get(self, request):
        form = ContributionForm()
        return render(request, 'core/pay.html', {'form': form})

    def post(self, request):
        form = ContributionForm(request.POST, request.FILES)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.membre = request.user
            contribution.statut = 'en_attente'
            contribution.save()
            messages.success(request, "Votre contribution a été envoyée pour validation.")
            return redirect('my_payments')
        return render(request, 'core/pay.html', {'form': form})


# ==========================================
# VALIDATION PAR STAFF
# ==========================================

@method_decorator(login_required, name='dispatch')
class ValiderContributionView(View):
    def get(self, request, pk):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Accès non autorisé")
            return redirect('dashboard')

        contribution = Contribution.objects.get(pk=pk)
        form = ValidationContributionForm(instance=contribution)
        return render(request, 'core/review_payment.html', {'contribution': contribution, 'form': form})

    def post(self, request, pk):
        contribution = Contribution.objects.get(pk=pk)
        form = ValidationContributionForm(request.POST, instance=contribution)
        if form.is_valid():
            if form.cleaned_data['statut'] == 'valide':
                contribution.valider(request.user)
                messages.success(request, f"Contribution de {contribution.membre.nom_complet} validée.")
            elif form.cleaned_data['statut'] == 'rejetee':
                contribution.rejeter(form.cleaned_data['commentaire'])
                messages.warning(request, f"Contribution de {contribution.membre.nom_complet} rejetée.")
            return redirect('dashboard')
        return render(request, 'core/review_payment.html', {'contribution': contribution, 'form': form})


# ==========================================
# GESTION DES COTISATIONS (STAFF)
# ==========================================

@method_decorator(login_required, name='dispatch')
class ListeCotisationsView(View):
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Accès non autorisé")
            return redirect('dashboard')
        cotisations = Cotisation.objects.all().select_related('cree_par').order_by('-date_debut')
        return render(request, 'core/dues.html', {'cotisations': cotisations})


@method_decorator(login_required, name='dispatch')
class CotisationCreateView(View):
    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Accès non autorisé")
            return redirect('dashboard')
        form = CotisationForm()
        return render(request, 'core/due_form.html', {'form': form})

    def post(self, request):
        form = CotisationForm(request.POST)
        if form.is_valid():
            cotisation = form.save(commit=False)
            cotisation.cree_par = request.user
            cotisation.save()
            messages.success(request, f"Cotisation '{cotisation.titre}' créée avec succès.")
            return redirect('dues')
        return render(request, 'core/due_form.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class CotisationDetailView(View):
    def get(self, request, pk):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Accès non autorisé")
            return redirect('dashboard')
        cotisation = Cotisation.objects.prefetch_related('contributions__membre').get(pk=pk)
        return render(request, 'core/due_detail.html', {
            'cotisation': cotisation,
            'contributions': cotisation.contributions.all()
        })


@method_decorator(login_required, name='dispatch')
class CotisationUpdateView(View):
    def get(self, request, pk):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Accès non autorisé")
            return redirect('dashboard')
        cotisation = Cotisation.objects.get(pk=pk)
        form = CotisationForm(instance=cotisation)
        return render(request, 'core/due_form.html', {'form': form})

    def post(self, request, pk):
        cotisation = Cotisation.objects.get(pk=pk)
        form = CotisationForm(request.POST, instance=cotisation)
        if form.is_valid():
            form.save()
            messages.success(request, f"Cotisation '{cotisation.titre}' mise à jour.")
            return redirect('dues')
        return render(request, 'core/due_form.html', {'form': form})
class CellulesView(View):
    def get(self, request):
        cellules = Cellule.objects.filter(est_active=True)
        return render(request, 'core/cellules.html', {'cellules': cellules})
@method_decorator(staff_member_required, name='dispatch')
class CelluleCreateView(View):
    def get(self, request):
        form = CelluleForm()
        return render(request, 'core/cellule_form.html', {'form': form})

    def post(self, request):
        form = CelluleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cellule créée avec succès.")
            return redirect('cellules')
        return render(request, 'core/cellule_form.html', {'form': form})