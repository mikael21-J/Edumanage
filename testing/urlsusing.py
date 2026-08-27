from django.urls import path
from . import views

urlpatterns = [
    path('verifier-identite/', views.verifier_identite_etudiant, name='verifier_identite'),
    path('creer-compte/', views.creer_compte_etudiant, name='creer_compte_etudiant'),
    path('login/', views.connexion_view, name='login'),
    path('logout/', views.deconnexion_view, name='logout'),
]