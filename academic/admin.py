
from django.contrib import admin
from .models import Faculte, Departement, Filiere, UE, EnseignantUE


@admin.register(Faculte)
class FaculteAdmin(admin.ModelAdmin):
    list_display = ('code_fac', 'nom_fac')
    search_fields = ('code_fac', 'nom_fac')


@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ('code_dept', 'nom_dept', 'faculte')
    list_filter = ('faculte',)
    search_fields = ('code_dept', 'nom_dept')


# Conserver les enregistrements existants pour Filiere, UE, EnseignantUE...

@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ('code_filiere', 'nom_filiere')
    search_fields = ('code_filiere', 'nom_filiere')


@admin.register(UE)
class UEAdmin(admin.ModelAdmin):
    list_display = ('code_ue', 'intitule', 'filiere', 'niveau', 'semestre', 'credits', 'avec_tp')
    list_filter = ('filiere', 'niveau', 'semestre', 'avec_tp')
    search_fields = ('code_ue', 'intitule')


@admin.register(EnseignantUE)
class EnseignantUEAdmin(admin.ModelAdmin):
    list_display = ('enseignant', 'ue', 'date_declaration')
    list_filter = ('ue__filiere', 'ue__niveau')
    search_fields = ('enseignant__nom', 'enseignant__matricule', 'ue__code_ue')
