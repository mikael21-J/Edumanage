from django.contrib import admin
from .models import InscriptionUE, Classe, Note
from .models import PV, PVNote, Requete


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


@admin.register(PV)
class PVAdmin(admin.ModelAdmin):
    list_display = ('ue', 'enseignant', 'annee_academique', 'etat', 'date_envoi', 'admin_traitement')
    list_filter = ('etat', 'annee_academique', 'ue__filiere', 'ue__niveau')
    search_fields = ('ue__code_ue', 'ue__intitule', 'enseignant__matricule')


@admin.register(PVNote)
class PVNoteAdmin(admin.ModelAdmin):
    list_display = ('pv', 'etudiant', 'cc', 'tp', 'sn')
    search_fields = ('etudiant__matricule', 'pv__ue__code_ue')


@admin.register(Requete)
class RequeteAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'ue', 'type_evaluation', 'motif', 'etat', 'date_envoi')
    list_filter = ('etat', 'motif', 'type_evaluation', 'ue__filiere')
    search_fields = ('etudiant__matricule', 'etudiant__nom', 'ue__code_ue')