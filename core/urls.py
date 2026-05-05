from django.urls import path
from . import views

urlpatterns = [
    # Pages publiques
    path('', views.AccueilView.as_view(), name='accueil'),
    path('a-propos/', views.AProposView.as_view(), name='a-propos'),
    path('nos-actions/', views.NosActionsView.as_view(), name='nos-actions'),
    path('realisations/', views.RealisationsView.as_view(), name='realisations'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # Authentification
    path('connexion/', views.ConnexionView.as_view(), name='connexion'),
    path('deconnexion/', views.DeconnexionView.as_view(), name='deconnexion'),
    
    # Adhésion (inscription)
    path('adhesion/', views.AdhesionView.as_view(), name='adhesion'),
    
    # Profil utilisateur (connecté)
    path('profil/', views.MonProfilView.as_view(), name='profil'),
    
    # Contributions (paiements des membres)
    path('mes-contributions/', views.MesContributionsView.as_view(), name='mes_contributions'),
    path('soumettre-contribution/', views.SoumettreContributionView.as_view(), name='soumettre_contribution'),
    
    # Cotisations (gestion admin/coordinateur)
    path('cotisations/', views.ListeCotisationsView.as_view(), name='liste_cotisations'),
    path('cotisations/creer/', views.CotisationCreateView.as_view(), name='creer_cotisation'),
    path('cotisations/<int:pk>/', views.CotisationDetailView.as_view(), name='cotisation_detail'),
    
    # Validation des contributions (coordinateur)
    path('valider-contribution/<int:pk>/', views.ValiderContributionView.as_view(), name='valider_contribution'),
    
    # Dashboard coordinateur
    path('dashboard-coordo/', views.DashboardCoordoView.as_view(), name='dashboard_coordo'),
]