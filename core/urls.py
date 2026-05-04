from django.urls import path
from . import views


urlpatterns = [
    path('', views.AccueilView.as_view(), name='accueil'),
    path('a-propos/', views.AProposView.as_view(), name='a-propos'),
    path('nos-actions/', views.NosActionsView.as_view(), name='nos-actions'),
    path('realisations/', views.RealisationsView.as_view(), name='realisations'),
    path('adhesion/', views.AdhesionView.as_view(), name='adhesion'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('connexion/', views.ConnexionView.as_view(), name='connexion'),
    path('deconnexion/', views.DeconnexionView.as_view(), name='deconnexion'),
    path('tableau-de-bord/', views.TableauBordView.as_view(), name='tableau-bord'),
    path('mes-cotisations/', views.MesCotisationsView.as_view(), name='mes_cotisations'),
    path('profil/', views.MonProfilView.as_view(), name='profil'),
    path('soumettre-cotisation/', views.SoumettreCotisationView.as_view(), name='soumettre_cotisation'),
]