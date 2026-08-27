from .models import Enseignant, Etudiant


def connected_person(request):
    role = request.session.get('auth_role')
    matricule = request.session.get('auth_matricule')
    person = None
    if role == 'etudiant' and matricule:
        person = Etudiant.objects.select_related('filiere').filter(matricule=matricule).first()
    elif role == 'enseignant' and matricule:
        person = Enseignant.objects.filter(matricule=matricule).first()
    return {'connected_person': person}
