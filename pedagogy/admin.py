from django.contrib import admin
from .models import InscriptionUE, Classe, Note


@admin.register(InscriptionUE)
class InscriptionUEAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'ue', 'annee_academique', 'date_inscription')
    list_filter = ('annee_academique', 'ue__filiere', 'ue__niveau')
    search_fields = ('etudiant__matricule', 'etudiant__nom', 'ue__code_ue')


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('ue', 'enseignant', 'annee_academique')
    list_filter = ('annee_academique', 'ue__filiere', 'ue__niveau')
    search_fields = ('ue__code_ue', 'enseignant__nom', 'enseignant__matricule')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'ue', 'type_evaluation', 'valeur_note', 'est_publie')
    list_filter = ('type_evaluation', 'est_publie', 'ue__filiere')
    search_fields = ('etudiant__matricule', 'etudiant__nom', 'ue__code_ue')