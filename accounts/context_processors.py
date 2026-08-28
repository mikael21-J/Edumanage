from .models import AdminCellule, Enseignant, Etudiant


def connected_person(request):
    role = request.session.get('auth_role')
    identifier = request.session.get('auth_identifier') or request.session.get('auth_matricule')
    person = None
    if role == 'etudiant' and identifier:
        person = Etudiant.objects.select_related('filiere').filter(matricule=identifier).first()
    elif role == 'enseignant' and identifier:
        person = Enseignant.objects.filter(matricule=identifier).first()
    elif role == 'admin_cellule' and identifier:
        person = AdminCellule.objects.filter(username=identifier).first()
    return {'connected_person': person}
