from django.contrib import admin
from .models import Etudiant, Enseignant


@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'niveau', 'filiere', 'region')
    search_fields = ('matricule', 'nom', 'prenom')
    list_filter = ('niveau', 'region')


@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'fonction')
    search_fields = ('matricule', 'nom', 'prenom')