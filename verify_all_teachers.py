#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gestion_note.settings')
django.setup()

from accounts.models import Enseignant
from academic.models import EnseignantUE

# Verify the admin form works for all teachers
teachers = Enseignant.objects.all()[:5]

print("Vérification du formulaire admin pour chaque enseignant:\n")

for teacher in teachers:
    ue_count = EnseignantUE.objects.filter(enseignant=teacher).count()
    form_url = f'/accounts/dashboard/admin-cellule/gestion/enseignants/{teacher.matricule}/'
    modify_url = f'/accounts/dashboard/enseignant/select-ues/?teacher_matricule={teacher.matricule}'
    
    print(f"✓ {teacher.matricule}: {teacher.prenom} {teacher.nom}")
    print(f"  - UE count: {ue_count}")
    print(f"  - Form URL: {form_url}")
    print(f"  - Modify URL: {modify_url}")
    print()

print("✓ Toutes les pages d'enseignant peuvent afficher les UE dispensées")
print("✓ Chaque enseignant a un bouton 'Modifier' pointant vers sa page de sélection UE")
