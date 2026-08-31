from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from academic.models import Departement, Faculte, Filiere, UE, EnseignantUE
from .models import AdminCellule, Etudiant, Enseignant
from pedagogy.models import EtatPV, EtatRequete, InscriptionUE, MotifRequete, Note, PV, PVNote, Requete, TypeEvaluation
from .forms import EtudiantForm, EnseignantForm, RequeteForm, UEForm, EnseignantProfileForm

def current_person(request, role=None):
    session_role = request.session.get('auth_role')
    identifier = request.session.get('auth_identifier') or request.session.get('auth_matricule')
    if role and session_role != role:
        return None
    model = {
        'etudiant': (Etudiant, 'matricule'),
        'enseignant': (Enseignant, 'matricule'),
        'admin_cellule': (AdminCellule, 'username'),
    }.get(session_role)
    return model[0].objects.filter(**{model[1]: identifier}).first() if model and identifier else None


def home(request):
    return render(request, 'home.html')


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
        model = Etudiant if role == 'etudiant' else Enseignant if role == 'enseignant' else AdminCellule if role == 'admin_cellule' else None
        lookup = 'username' if role == 'admin_cellule' else 'matricule'
        filters = {lookup: matricule}
        if role == 'admin_cellule':
            filters['actif'] = True
        person = model.objects.filter(**filters).first() if model else None
        if person and password_matches(person, password):
            request.session['auth_role'] = role
            request.session['auth_identifier'] = matricule
            request.session['auth_matricule'] = matricule
            if role == 'etudiant' and InscriptionUE.objects.filter(etudiant=person).count() < 7:
                return redirect('select_ues')
            return redirect({'etudiant': 'dashboard_etudiant', 'enseignant': 'dashboard_enseignant', 'admin_cellule': 'dashboard_admin_cellule'}[role])
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

    return render(request, 'student/select_ues.html', {
        'ues': ues_disponibles,
        'etudiant': etudiant,
        'selected_codes': selected_codes,
        'remaining_count': remaining_count,
        'faculte_choices': ues_disponibles.values('filiere__departement__faculte_id', 'filiere__departement__faculte__nom_fac').distinct().order_by('filiere__departement__faculte__nom_fac'),
        'departement_choices': ues_disponibles.values('filiere__departement_id', 'filiere__departement__nom_dept').distinct().order_by('filiere__departement__nom_dept'),
        'filiere_choices': ues_disponibles.values('filiere__code_filiere', 'filiere__nom_filiere').distinct().order_by('filiere__code_filiere'),
        'niveau_choices': ues_disponibles.values_list('niveau', flat=True).distinct().order_by('niveau'),
    })


def select_teacher_ues(request):
    admin_session = current_person(request, 'admin_cellule')
    teacher_session = current_person(request, 'enseignant')
    teacher_matricule = request.GET.get('teacher_matricule') or request.POST.get('teacher_matricule')

    if not admin_session and not teacher_session and not request.session.get('registration_matricule'):
        return redirect('login')

    if teacher_matricule:
        if not admin_session:
            messages.error(request, 'Seul l’administrateur cellule peut modifier les UE d’un enseignant.')
            return redirect('dashboard_enseignant')
        enseignant = get_object_or_404(Enseignant, matricule=teacher_matricule)
    elif request.session.get('registration_matricule'):
        enseignant = get_object_or_404(Enseignant, matricule=request.session.get('registration_matricule'))
    elif teacher_session:
        enseignant = teacher_session
    else:
        enseignant = admin_session and get_object_or_404(Enseignant, matricule=teacher_matricule) if teacher_matricule else None

    if enseignant is None:
        return redirect('dashboard_enseignant')

    ues = UE.objects.all().select_related('filiere', 'filiere__departement', 'filiere__departement__faculte').order_by('filiere__code_filiere', 'niveau', 'code_ue')
    current_codes = set(EnseignantUE.objects.filter(enseignant=enseignant).values_list('ue_id', flat=True))
    is_admin_edit = bool(admin_session and teacher_matricule)

    if request.method == 'POST':
        if not (admin_session or request.session.get('registration_matricule')) and not teacher_session:
            return redirect('login')
        if not admin_session and teacher_session and not request.session.get('registration_matricule'):
            messages.error(request, 'Vous ne pouvez pas modifier vos UE depuis cette page. Consultez votre profil.')
            return redirect('teacher_profile')
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
            if request.session.get('registration_matricule'):
                request.session.pop('registration_matricule', None)
                request.session.pop('user_role', None)
            if admin_session:
                return redirect('admin_resource_edit', resource='enseignants', object_id=enseignant.matricule)
            return redirect('dashboard_enseignant')
    return render(request, 'teacher/select_teacher_ues.html', {
        'ues': ues, 'enseignant': enseignant, 'current_codes': current_codes,
        'faculte_choices': ues.values('filiere__departement__faculte_id', 'filiere__departement__faculte__nom_fac').distinct().order_by('filiere__departement__faculte__nom_fac'),
        'departement_choices': ues.values('filiere__departement_id', 'filiere__departement__nom_dept').distinct().order_by('filiere__departement__nom_dept'),
        'filiere_choices': ues.values('filiere__code_filiere', 'filiere__nom_filiere').distinct().order_by('filiere__code_filiere'),
        'niveau_choices': ues.values_list('niveau', flat=True).distinct().order_by('niveau'),
        'is_admin_edit': is_admin_edit,
        'admin_cellule': admin_session,
    })


def dashboard_etudiant(request):
    if not current_person(request, 'etudiant'):
        return redirect('login')
    
    etudiant = current_person(request, 'etudiant')
    inscriptions = InscriptionUE.objects.filter(etudiant=etudiant).select_related('ue')
    if inscriptions.count() < 7:
        return redirect('select_ues')
    return render(request, 'student/dashboard_etudiant.html', {
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
    requetes = Requete.objects.filter(etudiant=etudiant, ue=code_ue)
    can_submit_requete = any(code in notes and code not in set(requetes.values_list('type_evaluation', flat=True)) for code, _ in TypeEvaluation.choices if code != 'RAT')
    return render(request, 'student/student_ue_detail.html', {
        'etudiant': etudiant, 'inscription': inscription, 'notes': notes,
        'evaluation_notes': [(code, label, notes.get(code)) for code, label in TypeEvaluation.choices],
        'evaluation_types': TypeEvaluation.choices,
        'requetes': requetes,
        'can_submit_requete': can_submit_requete,
    })


def student_requetes(request):
    if not current_person(request, 'etudiant'):
        return redirect('login')
    etudiant = current_person(request, 'etudiant')
    return render(request, 'student/student_requetes.html', {
        'etudiant': etudiant,
        'requetes': Requete.objects.filter(etudiant=etudiant).select_related('ue').order_by('-date_envoi'),
    })


def student_submit_requete(request, code_ue):
    if not current_person(request, 'etudiant'):
        return redirect('login')
    etudiant = current_person(request, 'etudiant')
    inscription = get_object_or_404(InscriptionUE.objects.select_related('ue'), etudiant=etudiant, ue_id=code_ue)
    published_notes = Note.objects.filter(etudiant=etudiant, ue=inscription.ue, est_publie=True).exclude(type_evaluation='RAT')
    published_types = [(note.type_evaluation, dict(TypeEvaluation.choices).get(note.type_evaluation, note.type_evaluation)) for note in published_notes]
    if not published_types:
        messages.warning(request, 'Vous devez avoir au moins une note publiée pour envoyer une requête.')
        return redirect('student_ue_detail', code_ue=code_ue)
    existing_types = set(Requete.objects.filter(etudiant=etudiant, ue=inscription.ue).values_list('type_evaluation', flat=True))
    available_types = [choice for choice in published_types if choice[0] not in existing_types]
    if request.method == 'POST':
        form = RequeteForm(request.POST, published_types=available_types)
        if form.is_valid():
            evaluation_type = form.cleaned_data['type_evaluation']
            if evaluation_type in existing_types or not published_notes.filter(type_evaluation=evaluation_type).exists():
                form.add_error('type_evaluation', 'Cette note possède déjà une requête ou n’est pas publiée.')
            else:
                requete = form.save(commit=False)
                requete.etudiant = etudiant
                requete.ue = inscription.ue
                requete.enseignant = get_object_or_404(EnseignantUE, ue=inscription.ue).enseignant
                requete.save()
                messages.success(request, 'Votre requête a bien été envoyée à l’enseignant.')
                return redirect('student_ue_detail', code_ue=code_ue)
    else:
        form = RequeteForm(published_types=available_types)
    return render(request, 'student/student_submit_requete.html', {'etudiant': etudiant, 'inscription': inscription, 'form': form, 'available_types': available_types})


def teacher_requetes(request):
    if not current_person(request, 'enseignant'):
        return redirect('login')
    enseignant = current_person(request, 'enseignant')
    requetes = Requete.objects.filter(enseignant=enseignant, etat=EtatRequete.ENVOYEE).select_related('etudiant__filiere', 'ue__filiere__departement').order_by('-date_envoi')
    return render(request, 'teacher/teacher_requetes.html', {'enseignant': enseignant, 'requetes': requetes})


def teacher_requete_detail(request, requete_id):
    if not current_person(request, 'enseignant'):
        return redirect('login')
    enseignant = current_person(request, 'enseignant')
    requete = get_object_or_404(Requete.objects.select_related('etudiant__filiere__departement', 'ue'), pk=requete_id, enseignant=enseignant, etat=EtatRequete.ENVOYEE)
    if request.method == 'POST' and request.POST.get('action') == 'validate':
        requete.etat = EtatRequete.VALIDEE
        requete.date_validation = timezone.now()
        requete.save(update_fields=('etat', 'date_validation'))
        messages.success(request, 'La requête a été validée.')
        return redirect('teacher_requetes')
    return render(request, 'teacher/teacher_requete_detail.html', {'enseignant': enseignant, 'requete': requete})


def teacher_profile(request):
    if not current_person(request, 'enseignant'):
        return redirect('login')

    enseignant = current_person(request, 'enseignant')
    habilitations = EnseignantUE.objects.filter(enseignant=enseignant).select_related('ue', 'ue__filiere__departement__faculte').order_by('ue__filiere__code_filiere', 'ue__code_ue')

    if request.method == 'POST':
        form = EnseignantProfileForm(request.POST, instance=enseignant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vos informations ont bien été mises à jour.')
            return redirect('teacher_profile')
    else:
        form = EnseignantProfileForm(instance=enseignant)

    return render(request, 'teacher/teacher_profile.html', {
        'enseignant': enseignant,
        'form': form,
        'habilitations': habilitations,
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
    return render(request, 'teacher/dashboard_enseignant.html', {'enseignant': enseignant, 'habilitations': habilitations})


def teacher_evaluations(request, code_ue):
    if not current_person(request, 'enseignant'):
        return redirect('login')
    enseignant = current_person(request, 'enseignant')
    ue = get_object_or_404(UE, code_ue=code_ue)
    if not EnseignantUE.objects.filter(enseignant=enseignant, ue=ue).exists():
        messages.error(request, "Vous n'êtes pas habilité à gérer cette UE.")
        return redirect('dashboard_enseignant')
    return render(request, 'teacher/teacher_evaluations.html', {
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
                    defaults={'valeur_note': value, 'est_publie': evaluation_type in {'CC', 'TP'}}
                )
        if errors:
            messages.error(request, "Notes invalides pour : " + ', '.join(errors))
        else:
            message = "Les notes ont été enregistrées et publiées." if evaluation_type in {'CC', 'TP'} else "Les notes de SN ont été enregistrées. Elles restent privées jusqu'à la publication du PV."
            messages.success(request, message)
        return redirect('teacher_gradebook', code_ue=code_ue, evaluation_type=evaluation_type)
    student_rows = [(student, existing.get(student.matricule)) for student in students]
    return render(request, 'teacher/teacher_gradebook.html', {
        'ue': ue, 'student_rows': student_rows,
        'evaluation_type': evaluation_type,
        'evaluation_choices': TypeEvaluation.choices,
        'evaluation_label': dict(TypeEvaluation.choices).get(evaluation_type, evaluation_type),
    })


def teacher_impress(request, code_ue, evaluation_type):
    if not current_person(request, 'enseignant'):
        return redirect('login')

    enseignant = current_person(request, 'enseignant')
    ue = get_object_or_404(UE.objects.select_related('filiere__departement__faculte'), code_ue=code_ue)
    if not EnseignantUE.objects.filter(enseignant=enseignant, ue=ue).exists():
        messages.error(request, "Vous n'êtes pas habilité à gérer cette UE.")
        return redirect('dashboard_enseignant')

    valid_types = {value for value, _ in TypeEvaluation.choices}
    if evaluation_type not in valid_types:
        return redirect('teacher_evaluations', code_ue=code_ue)

    students = Etudiant.objects.filter(inscriptions__ue=ue).distinct().order_by('nom', 'prenom')
    notes = {note.etudiant_id: note for note in Note.objects.filter(ue=ue, type_evaluation=evaluation_type)}
    rows = [(student, notes.get(student.matricule)) for student in students]

    return render(request, 'teacher/impress.html', {
        'enseignant': enseignant,
        'ue': ue,
        'rows': rows,
        'evaluation_type': evaluation_type,
        'evaluation_label': dict(TypeEvaluation.choices).get(evaluation_type, evaluation_type),
        'evaluation_choices': TypeEvaluation.choices,
    })


def teacher_pv(request, code_ue):
    if not current_person(request, 'enseignant'):
        return redirect('login')
    enseignant = current_person(request, 'enseignant')
    ue = get_object_or_404(UE, code_ue=code_ue)
    if not EnseignantUE.objects.filter(enseignant=enseignant, ue=ue).exists():
        messages.error(request, "Vous n'êtes pas habilité à gérer cette UE.")
        return redirect('dashboard_enseignant')
    students = list(Etudiant.objects.filter(inscriptions__ue=ue).distinct().order_by('nom', 'prenom'))
    notes = Note.objects.filter(ue=ue, etudiant__in=students).values('etudiant_id', 'type_evaluation', 'valeur_note')
    note_map = {(row['etudiant_id'], row['type_evaluation']): row['valeur_note'] for row in notes}
    pv = PV.objects.filter(ue=ue).first()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'send':
            missing = [student.matricule for student in students if note_map.get((student.matricule, 'SN')) is None]
            if missing:
                messages.error(request, 'La note SN manque pour : ' + ', '.join(missing))
            else:
                with transaction.atomic():
                    pv, _ = PV.objects.update_or_create(
                        ue=ue, annee_academique='2025-2026',
                        defaults={'enseignant': enseignant, 'etat': EtatPV.ENVOYE,
                                  'date_envoi': timezone.now(), 'commentaire_rejet': ''}
                    )
                    PVNote.objects.filter(pv=pv).delete()
                    PVNote.objects.bulk_create([
                        PVNote(pv=pv, etudiant=student,
                               cc=note_map.get((student.matricule, 'CC')),
                               tp=note_map.get((student.matricule, 'TP')),
                               sn=note_map.get((student.matricule, 'SN')))
                        for student in students
                    ])
                messages.success(request, 'Le PV a été envoyé à la cellule informatique.')
        return redirect('teacher_pv', code_ue=code_ue)
    rows = [(student, note_map.get((student.matricule, 'CC')), note_map.get((student.matricule, 'TP')), note_map.get((student.matricule, 'SN'))) for student in students]
    return render(request, 'teacher/teacher_pv.html', {'ue': ue, 'enseignant': enseignant, 'rows': rows, 'pv': pv})


def dashboard_admin_cellule(request):
    admin_cellule = current_person(request, 'admin_cellule')
    if not admin_cellule:
        return redirect('login')
    pvs = PV.objects.select_related('ue__filiere__departement__faculte', 'enseignant').filter(etat=EtatPV.ENVOYE)
    filters = {key: request.GET.get(key, '').strip() for key in ('faculte', 'departement', 'filiere', 'niveau')}
    if filters['faculte']:
        pvs = pvs.filter(ue__filiere__departement__faculte_id=filters['faculte'])
    if filters['departement']:
        pvs = pvs.filter(ue__filiere__departement_id=filters['departement'])
    if filters['filiere']:
        pvs = pvs.filter(ue__filiere_id=filters['filiere'])
    if filters['niveau']:
        pvs = pvs.filter(ue__niveau=filters['niveau'])
    return render(request, 'admin_cellule/dashboard_admin_cellule.html', {
        'admin_cellule': admin_cellule, 'pvs': pvs,
        'facultes': Faculte.objects.all(), 'departements': Departement.objects.all(),
        'filieres': Filiere.objects.all(), 'niveaux': UE._meta.get_field('niveau').choices,
        'filters': filters, 'stats': {'pending': PV.objects.filter(etat=EtatPV.ENVOYE).count(), 'students': Etudiant.objects.count(), 'ues': UE.objects.count()}
    })


def admin_pv_detail(request, pv_id):
    admin_cellule = current_person(request, 'admin_cellule')
    if not admin_cellule:
        return redirect('login')
    pv = get_object_or_404(PV.objects.select_related('ue', 'enseignant'), pk=pv_id)
    if request.method == 'POST' and pv.etat == EtatPV.ENVOYE:
        action = request.POST.get('action')
        if action == 'publish':
            with transaction.atomic():
                for row in pv.lignes.all():
                    for evaluation_type, value in (('CC', row.cc), ('TP', row.tp), ('SN', row.sn)):
                        if value is not None:
                            Note.objects.update_or_create(etudiant=row.etudiant, ue=pv.ue, type_evaluation=evaluation_type, defaults={'valeur_note': value, 'est_publie': True})
                pv.etat = EtatPV.PUBLIE
                pv.admin_traitement = admin_cellule
                pv.date_traitement = timezone.now()
                pv.save(update_fields=('etat', 'admin_traitement', 'date_traitement'))
            messages.success(request, 'Le PV est publié. Les notes sont maintenant visibles par les étudiants.')
        elif action == 'reject':
            pv.etat = EtatPV.REJETE
            pv.commentaire_rejet = request.POST.get('commentaire_rejet', '').strip()
            if not pv.commentaire_rejet:
                messages.error(request, 'Un motif de rejet est obligatoire.')
            else:
                pv.admin_traitement = admin_cellule
                pv.date_traitement = timezone.now()
                pv.save(update_fields=('etat', 'commentaire_rejet', 'admin_traitement', 'date_traitement'))
                messages.success(request, 'Le PV a été rejeté avec son motif.')
                return redirect('dashboard_admin_cellule')
            return redirect('admin_pv_detail', pv_id=pv.id)
    return render(request, 'admin_cellule/admin_pv_detail.html', {'admin_cellule': admin_cellule, 'pv': pv, 'rows': pv.lignes.select_related('etudiant').all()})


def admin_pv_list(request):
    """Liste des PV publiés par l'adminCellule connecté"""
    admin_cellule = current_person(request, 'admin_cellule')
    if not admin_cellule:
        return redirect('login')
    
    # Récupérer tous les PV publiés traités par cet adminCellule
    pvs = PV.objects.select_related('ue__filiere__departement__faculte', 'enseignant', 'admin_traitement').filter(
        etat=EtatPV.PUBLIE,
        admin_traitement=admin_cellule
    ).order_by('-date_traitement')
    
    # Filtres
    filters = {key: request.GET.get(key, '').strip() for key in ('faculte', 'departement', 'filiere', 'niveau')}
    if filters['faculte']:
        pvs = pvs.filter(ue__filiere__departement__faculte_id=filters['faculte'])
    if filters['departement']:
        pvs = pvs.filter(ue__filiere__departement_id=filters['departement'])
    if filters['filiere']:
        pvs = pvs.filter(ue__filiere_id=filters['filiere'])
    if filters['niveau']:
        pvs = pvs.filter(ue__niveau=filters['niveau'])
    
    # Recherche
    query = request.GET.get('q', '').strip()
    if query:
        from django.db.models import Q
        pvs = pvs.filter(Q(ue__code_ue__icontains=query) | Q(ue__intitule__icontains=query) | Q(enseignant__nom__icontains=query))
    
    return render(request, 'admin_cellule/admin_pv_list.html', {
        'admin_cellule': admin_cellule,
        'pvs': pvs,
        'facultes': Faculte.objects.all(),
        'departements': Departement.objects.all(),
        'filieres': Filiere.objects.all(),
        'niveaux': UE._meta.get_field('niveau').choices,
        'filters': filters,
        'query': query
    })


def admin_resource(request, resource, object_id=None):
    if not current_person(request, 'admin_cellule'):
        return redirect('login')
    configs = {
        'ue': (UE, UEForm, 'UE', 'code_ue', ('code_ue', 'intitule')),
        'enseignants': (Enseignant, EnseignantForm, 'Enseignants', 'matricule', ('matricule', 'nom', 'prenom')),
        'etudiants': (Etudiant, EtudiantForm, 'Étudiants', 'matricule', ('matricule', 'nom', 'prenom')),
    }
    config = configs.get(resource)
    if not config:
        return redirect('dashboard_admin_cellule')
    model, form_class, label, pk_field, search_fields = config
    instance = get_object_or_404(model, **{pk_field: object_id}) if object_id else None
    if request.method == 'POST':
        if request.POST.get('action') == 'delete' and instance:
            instance.delete()
            messages.success(request, f'{label[:-1] if label.endswith("s") else label} supprimé(e).')
            return redirect('admin_resource', resource=resource)
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, f'{label[:-1] if label.endswith("s") else label} enregistré(e).')
            return redirect('admin_resource', resource=resource)
    else:
        form = form_class(instance=instance)
    items = model.objects.all()
    filter_values = {key: request.GET.get(key, '').strip() for key in ('faculte', 'departement', 'filiere', 'niveau', 'fonction')}
    if resource == 'ue':
        items = items.select_related('filiere__departement__faculte')
        if filter_values['faculte']:
            items = items.filter(filiere__departement__faculte_id=filter_values['faculte'])
        if filter_values['departement']:
            items = items.filter(filiere__departement_id=filter_values['departement'])
        if filter_values['filiere']:
            items = items.filter(filiere_id=filter_values['filiere'])
        if filter_values['niveau']:
            items = items.filter(niveau=filter_values['niveau'])
    elif resource == 'etudiants':
        items = items.select_related('filiere__departement__faculte')
        if filter_values['faculte']:
            items = items.filter(filiere__departement__faculte_id=filter_values['faculte'])
        if filter_values['departement']:
            items = items.filter(filiere__departement_id=filter_values['departement'])
        if filter_values['filiere']:
            items = items.filter(filiere_id=filter_values['filiere'])
        if filter_values['niveau']:
            items = items.filter(niveau=filter_values['niveau'])
    elif resource == 'enseignants' and filter_values['fonction']:
        items = items.filter(fonction__icontains=filter_values['fonction'])
    query = request.GET.get('q', '').strip()
    if query:
        from django.db.models import Q
        condition = Q()
        for field in search_fields:
            condition |= Q(**{f'{field}__icontains': query})
        items = items.filter(condition)
    template = 'admin_cellule/admin_resource_form.html' if instance or request.GET.get('new') == '1' else 'admin_cellule/admin_resource.html'
    context = {'label': label, 'resource': resource, 'items': items, 'form': form, 'editing': bool(instance), 'instance': instance, 'query': query, 'pk_field': pk_field, 'admin_cellule': current_person(request, 'admin_cellule'), 'filters': filter_values}
    if resource == 'enseignants' and instance:
        context['teacher_ues'] = EnseignantUE.objects.filter(enseignant=instance).select_related('ue', 'ue__filiere__departement__faculte').order_by('ue__filiere__code_filiere', 'ue__code_ue')
    context.update({'facultes': Faculte.objects.all(), 'departements': Departement.objects.all(), 'filieres': Filiere.objects.all(), 'niveaux': UE._meta.get_field('niveau').choices, 'fonctions': Enseignant.objects.values_list('fonction', flat=True).distinct().order_by('fonction')})
    return render(request, template, context)