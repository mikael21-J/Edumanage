from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404
from academic.models import UE, EnseignantUE
from .models import Etudiant, Enseignant
from pedagogy.models import InscriptionUE, Note, TypeEvaluation

def current_person(request, role=None):
    session_role = request.session.get('auth_role')
    matricule = request.session.get('auth_matricule')
    if role and session_role != role:
        return None
    model = Etudiant if session_role == 'etudiant' else Enseignant if session_role == 'enseignant' else None
    return model.objects.filter(matricule=matricule).first() if model and matricule else None


def password_matches(person, password):
    if not person.mot_de_passe:
        return False
    if check_password(password, person.mot_de_passe):
        return True
    # Convertit les anciens mots de passe enregistrés avant le hashage Django.
    if person.mot_de_passe == password:
        person.mot_de_passe = make_password(password)
        person.save(update_fields=['mot_de_passe'])
        return True
    return False


def user_login(request):
    if request.method == 'POST':
        role = request.POST.get('role', '').strip().lower()
        matricule = request.POST.get('matricule', '').strip()
        password = request.POST.get('password', '')
        model = Etudiant if role == 'etudiant' else Enseignant if role == 'enseignant' else None
        person = model.objects.filter(matricule=matricule).first() if model else None
        if person and password_matches(person, password):
            request.session['auth_role'] = role
            request.session['auth_matricule'] = matricule
            if role == 'etudiant' and InscriptionUE.objects.filter(etudiant=person).count() < 7:
                return redirect('select_ues')
            return redirect('dashboard_etudiant' if role == 'etudiant' else 'dashboard_enseignant')
        messages.error(request, "Rôle, matricule ou mot de passe incorrect.")
            
    return render(request, 'accounts/login.html')


def user_logout(request):
    request.session.flush()
    return redirect('login')


def check_identity(request):
    """Étape 1 : vérification du matricule étudiant ou enseignant."""
    if request.method == 'POST':
        matricule = request.POST.get('matricule', '').strip()
        etudiant = Etudiant.objects.filter(matricule=matricule).first()
        enseignant = Enseignant.objects.filter(matricule=matricule).first()

        if etudiant:
            if etudiant.mot_de_passe:
                messages.warning(request, "Ce compte existe déjà. Veuillez vous connecter.")
                return redirect('login')
            request.session['registration_matricule'] = etudiant.matricule
            request.session['user_role'] = 'etudiant'
            return redirect('create_password')
        if enseignant:
            if enseignant.mot_de_passe:
                messages.warning(request, "Ce compte existe déjà. Veuillez vous connecter.")
                return redirect('login')
            request.session['registration_matricule'] = enseignant.matricule
            request.session['user_role'] = 'enseignant'
            return redirect('create_password')

        messages.error(request, "Aucun utilisateur ne correspond à ce matricule.")
            
    return render(request, 'accounts/check_identity.html')


def create_password(request):
    """Étape 2 : Création du compte User et attribution du mot de passe"""
    matricule = request.session.get('registration_matricule')
    role = request.session.get('user_role')

    if not matricule or role not in {'etudiant', 'enseignant'}:
        messages.error(request, "Veuillez d'abord vérifier votre identité.")
        return redirect('check_identity')

    if request.method == 'POST':
        pwd1 = request.POST.get('password')
        pwd2 = request.POST.get('password_confirm')

        if pwd1 != pwd2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
        elif len(pwd1) < 6:
            messages.error(request, "Le mot de passe doit contenir au moins 6 caractères.")
        else:
            person = get_object_or_404(
                Etudiant if role == 'etudiant' else Enseignant,
                matricule=matricule
            )
            person.mot_de_passe = make_password(pwd1)
            person.save(update_fields=['mot_de_passe'])
            request.session['auth_role'] = role
            request.session['auth_matricule'] = matricule

            if role == 'etudiant':
                return redirect('select_ues')
            else:
                return redirect('select_teacher_ues')

    return render(request, 'accounts/create_password.html')


def select_ues(request):
    """Étape 3 : Inscription aux UE pour l'étudiant connecté"""
    if not current_person(request, 'etudiant'):
        return redirect('login')

    etudiant = current_person(request, 'etudiant')
    selected_codes = set(InscriptionUE.objects.filter(etudiant=etudiant).values_list('ue_id', flat=True))
    remaining_count = 7 - len(selected_codes)
    if remaining_count <= 0:
        return redirect('dashboard_etudiant')
    ues_disponibles = UE.objects.filter(filiere=etudiant.filiere, niveau=etudiant.niveau)

    if request.method == 'POST':
        submitted_codes = set(request.POST.getlist('ues'))
        valid_codes = set(ues_disponibles.values_list('code_ue', flat=True))
        existing_codes = set(InscriptionUE.objects.filter(etudiant=etudiant).values_list('ue_id', flat=True))
        if submitted_codes & existing_codes:
            messages.error(request, "Les UE déjà sélectionnées ne peuvent pas être modifiées.")
        elif len(submitted_codes) != 7 - len(existing_codes):
            messages.error(request, f"Sélectionnez encore {7 - len(existing_codes)} UE.")
        elif not submitted_codes.issubset(valid_codes - existing_codes):
            messages.error(request, "La sélection contient une UE non autorisée.")
        else:
            with transaction.atomic():
                InscriptionUE.objects.bulk_create([
                    InscriptionUE(etudiant=etudiant, ue_id=code_ue) for code_ue in submitted_codes
                ])

            request.session.pop('registration_matricule', None)
            request.session.pop('user_role', None)
            messages.success(request, "Inscription réussie ! Bienvenue sur votre espace.")
            return redirect('dashboard_etudiant')

    return render(request, 'accounts/select_ues.html', {
        'ues': ues_disponibles,
        'etudiant': etudiant,
        'selected_codes': selected_codes,
        'remaining_count': remaining_count,
    })


def select_teacher_ues(request):
    if not current_person(request, 'enseignant'):
        return redirect('login')
    enseignant = current_person(request, 'enseignant')
    ues = UE.objects.all().select_related('filiere').order_by('filiere__code_filiere', 'niveau', 'code_ue')
    current_codes = set(EnseignantUE.objects.filter(enseignant=enseignant).values_list('ue_id', flat=True))
    if request.method == 'POST':
        selected_codes = set(request.POST.getlist('ues'))
        valid_codes = set(ues.values_list('code_ue', flat=True))
        if not selected_codes or not selected_codes.issubset(valid_codes):
            messages.error(request, "Sélectionnez au moins une UE valide.")
        else:
            with transaction.atomic():
                EnseignantUE.objects.filter(enseignant=enseignant).exclude(ue_id__in=selected_codes).delete()
                EnseignantUE.objects.bulk_create([
                    EnseignantUE(enseignant=enseignant, ue_id=code) for code in selected_codes
                ], ignore_conflicts=True)
            request.session.pop('registration_matricule', None)
            request.session.pop('user_role', None)
            return redirect('dashboard_enseignant')
    return render(request, 'accounts/select_teacher_ues.html', {
        'ues': ues, 'enseignant': enseignant, 'current_codes': current_codes,
        'filiere_choices': ues.values('filiere__code_filiere', 'filiere__nom_filiere').distinct().order_by('filiere__code_filiere'),
        'niveau_choices': ues.values_list('niveau', flat=True).distinct().order_by('niveau'),
    })


def dashboard_etudiant(request):
    if not current_person(request, 'etudiant'):
        return redirect('login')
    
    etudiant = current_person(request, 'etudiant')
    inscriptions = InscriptionUE.objects.filter(etudiant=etudiant).select_related('ue')
    if inscriptions.count() < 7:
        return redirect('select_ues')
    return render(request, 'accounts/dashboard_etudiant.html', {
        'etudiant': etudiant,
        'inscriptions': inscriptions
    })


def student_ue_detail(request, code_ue):
    if not current_person(request, 'etudiant'):
        return redirect('login')
    etudiant = current_person(request, 'etudiant')
    inscription = get_object_or_404(
        InscriptionUE.objects.select_related('ue'), etudiant=etudiant, ue_id=code_ue
    )
    notes = {
        note.type_evaluation: note for note in Note.objects.filter(
            etudiant=etudiant, ue_id=code_ue, est_publie=True
        )
    }
    return render(request, 'accounts/student_ue_detail.html', {
        'etudiant': etudiant, 'inscription': inscription, 'notes': notes,
        'evaluation_notes': [(code, label, notes.get(code)) for code, label in TypeEvaluation.choices],
        'evaluation_types': TypeEvaluation.choices,
    })


def dashboard_enseignant(request):
    if not current_person(request, 'enseignant'):
        return redirect('login')
    
    enseignant = current_person(request, 'enseignant')
    habilitations = EnseignantUE.objects.filter(enseignant=enseignant).select_related('ue', 'ue__filiere').prefetch_related('ue__inscriptions_etudiants')
    for habilitation in habilitations:
        habilitation.student_count = len(habilitation.ue.inscriptions_etudiants.all())
        habilitation.published_count = Note.objects.filter(
            ue=habilitation.ue, est_publie=True
        ).values('etudiant').distinct().count()
        habilitation.progress = round(
            habilitation.published_count / habilitation.student_count * 100
        ) if habilitation.student_count else 0
    return render(request, 'accounts/dashboard_enseignant.html', {'enseignant': enseignant, 'habilitations': habilitations})


def teacher_evaluations(request, code_ue):
    if not current_person(request, 'enseignant'):
        return redirect('login')
    enseignant = current_person(request, 'enseignant')
    ue = get_object_or_404(UE, code_ue=code_ue)
    if not EnseignantUE.objects.filter(enseignant=enseignant, ue=ue).exists():
        messages.error(request, "Vous n'êtes pas habilité à gérer cette UE.")
        return redirect('dashboard_enseignant')
    return render(request, 'accounts/teacher_evaluations.html', {
        'ue': ue, 'enseignant': enseignant, 'evaluation_choices': TypeEvaluation.choices,
    })


def teacher_gradebook(request, code_ue, evaluation_type):
    if not current_person(request, 'enseignant'):
        return redirect('login')
    enseignant = current_person(request, 'enseignant')
    ue = get_object_or_404(UE, code_ue=code_ue)
    if not EnseignantUE.objects.filter(enseignant=enseignant, ue=ue).exists():
        messages.error(request, "Vous n'êtes pas habilité à gérer cette UE.")
        return redirect('dashboard_enseignant')
    valid_types = {value for value, _ in TypeEvaluation.choices}
    if evaluation_type not in valid_types:
        return redirect('teacher_evaluations', code_ue=code_ue)
    students = Etudiant.objects.filter(inscriptions__ue=ue).distinct().order_by('nom', 'prenom')
    existing = {
        note.etudiant_id: note for note in Note.objects.filter(ue=ue, type_evaluation=evaluation_type)
    }
    if request.method == 'POST':
        errors = []
        with transaction.atomic():
            for student in students:
                raw_value = request.POST.get(f'note_{student.matricule}', '').strip()
                if not raw_value:
                    continue
                try:
                    value = float(raw_value)
                except ValueError:
                    errors.append(student.matricule)
                    continue
                if not 0 <= value <= 20:
                    errors.append(student.matricule)
                    continue
                Note.objects.update_or_create(
                    etudiant=student, ue=ue, type_evaluation=evaluation_type,
                    defaults={'valeur_note': value, 'est_publie': True}
                )
        if errors:
            messages.error(request, "Notes invalides pour : " + ', '.join(errors))
        else:
            messages.success(request, "Les notes ont été enregistrées et publiées.")
        return redirect('teacher_gradebook', code_ue=code_ue, evaluation_type=evaluation_type)
    student_rows = [(student, existing.get(student.matricule)) for student in students]
    return render(request, 'accounts/teacher_gradebook.html', {
        'ue': ue, 'student_rows': student_rows,
        'evaluation_type': evaluation_type,
        'evaluation_choices': TypeEvaluation.choices,
        'evaluation_label': dict(TypeEvaluation.choices).get(evaluation_type, evaluation_type),
    })