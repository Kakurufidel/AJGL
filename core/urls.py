from django.urls import path
from . import views

urlpatterns = [
    path('', views.AccueilView.as_view(), name='accueil'),
    path('a-propos/', views.AProposView.as_view(), name='a-propos'),
    path('nos-actions/', views.NosActionsView.as_view(), name='nos-actions'),
    path('realisations/', views.RealisationsView.as_view(), name='realisations'),
    path('adhesion/', views.AdhesionView.as_view(), name='adhesion'),
    path('don/', views.DonView.as_view(), name='don'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('connexion/', views.ConnexionView.as_view(), name='connexion'),
    path('deconnexion/', views.DeconnexionView.as_view(), name='deconnexion'),
    path('tableau-de-bord/', views.TableauBordView.as_view(), name='tableau-bord'),
]