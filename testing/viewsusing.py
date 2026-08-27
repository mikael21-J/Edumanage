from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Etudiant, Utilisateur, RoleUtilisateur


def verifier_identite_etudiant(request):
    """
    Étape 1 : L'étudiant saisit ses informations personnelles pour vérification.
    """
    if request.method == 'POST':
        matricule = request.POST.get('matricule')
        nom = request.POST.get('nom')
        date_naissance = request.POST.get('date_naissance')

        try:
            etudiant = Etudiant.objects.get(
                matricule=matricule,
                nom__iexact=nom,
                date_naissance=date_naissance
            )
            # Vérifier si un compte existe déjà pour ce matricule
            if Utilisateur.objects.filter(matricule=matricule).exists():
                messages.error(request, "Un compte existe déjà pour ce matricule.")
                return redirect('login')

            # Stocker le matricule en session pour l'étape de création de mot de passe
            request.session['matricule_verification'] = etudiant.matricule
            return redirect('creer_compte_etudiant')

        except Etudiant.DoesNotExist:
            messages.error(request, "Informations incorrectes. Impossible de vérifier votre identité.")

    return render(request, 'accounts/verifier_identite.html')


def creer_compte_etudiant(request):
    """
    Étape 2 : Création du compte utilisateur après vérification réussie.
    """
    matricule = request.session.get('matricule_verification')
    if not matricule:
        return redirect('verifier_identite')

    etudiant = Etudiant.objects.get(matricule=matricule)

    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
        else:
            # Format automatique du username : prenom.nom
            username = f"{etudiant.prenom.lower()}.{etudiant.nom.lower()}".replace(" ", "")
            
            # Gestion des doublons de username
            count = 1
            original_username = username
            while Utilisateur.objects.filter(username=username).exists():
                username = f"{original_username}{count}"
                count += 1

            utilisateur = Utilisateur.objects.create_user(
                username=username,
                password=password,
                role=RoleUtilisateur.ETUDIANT,
                matricule=etudiant.matricule
            )
            
            # Nettoyer la session et connecter l'utilisateur
            del request.session['matricule_verification']
            login(request, utilisateur)
            
            # Redirection vers la sélection des UE
            return redirect('selection_ue')

    return render(request, 'accounts/creer_compte.html', {'etudiant': etudiant})


def connexion_view(request):
    """
    Vue de connexion universelle (Étudiant & Enseignant).
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == RoleUtilisateur.ETUDIANT:
                return redirect('dashboard_etudiant')
            else:
                return redirect('dashboard_enseignant')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, 'accounts/login.html')


def deconnexion_view(request):
    logout(request)
    return redirect('login')