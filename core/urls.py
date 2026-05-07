from django.urls import path
from . import views

urlpatterns = [
    path('', views.AccueilView.as_view(), name='home'),
    path('about/', views.AProposView.as_view(), name='about'),
    path('actions/', views.NosActionsView.as_view(), name='actions'),
    path('achievements/', views.RealisationsView.as_view(), name='achievements'),
    path('register/', views.AdhesionView.as_view(), name='register'),
    path('login/', views.ConnexionView.as_view(), name='login'),
    path('logout/', views.DeconnexionView.as_view(), name='logout'),
    path('profile/', views.MonProfilView.as_view(), name='profile'),
    path('my-payments/', views.MesContributionsView.as_view(), name='my_payments'),
    path('pay/', views.SoumettreContributionView.as_view(), name='pay'),
    path('dues/', views.ListeCotisationsView.as_view(), name='dues'),
    path('due/create/', views.CotisationCreateView.as_view(), name='due_create'),
    path('due/<int:pk>/', views.CotisationDetailView.as_view(), name='due_detail'),
    path('review/<int:pk>/', views.ValiderContributionView.as_view(), name='review_payment'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path("contact/",views.ContactView.as_view(), name='contact')

]