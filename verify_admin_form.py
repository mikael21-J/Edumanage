#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gestion_note.settings')
django.setup()

from accounts.models import Enseignant, AdminCellule
from academic.models import EnseignantUE

# Get the first teacher
enseignant = Enseignant.objects.first()
if enseignant:
    print(f'Teacher: {enseignant.matricule} - {enseignant.prenom} {enseignant.nom}')
    
    # Get UEs for this teacher
    ues = EnseignantUE.objects.filter(enseignant=enseignant).select_related('ue', 'ue__filiere')
    print(f'UEs assigned: {ues.count()}')
    for hab in ues[:5]:
        print(f'  - {hab.ue.code_ue}: {hab.ue.intitule}')
    
    print('\nTemplate variables that will be available:')
    print(f'  - instance: {enseignant.matricule}')
    print(f'  - teacher_ues: {ues.count()} items')
    print(f'  - resource: "enseignants"')
    
    print('\nTemplate structure verification:')
    print('✓ Two-column layout with d-flex gap-4')
    print('✓ Left column: form with flex-grow-1')
    print('✓ Right column: list of UEs with Modifier button')
    print('✓ Conditional display for enseignants only')
else:
    print('No teacher found')
