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


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.management import call_command

@csrf_exempt
def migrate_view(request):
    if request.GET.get('key') == 'MAGIC_KEY_123':
        call_command('migrate', interactive=False)
        return JsonResponse({'status': 'migrations done'})
    return JsonResponse({'error': 'unauthorized'}, status=401)

urlpatterns += [
    path('secret-migrate/', migrate_view, name='migrate'),
]