from django.db import models


class RoleUtilisateur(models.TextChoices):
    ETUDIANT = 'ETUDIANT', 'Étudiant'
    ENSEIGNANT = 'ENSEIGNANT', 'Enseignant'


class Region(models.TextChoices):
    ADAMAOUA = 'ADAMAOUA', 'Adamaoua'
    CENTRE = 'CENTRE', 'Centre'
    EST = 'EST', 'Est'
    EXTREME_NORD = 'EXTREME_NORD', 'Extrême-Nord'
    LITTORAL = 'LITTORAL', 'Littoral'
    NORD = 'NORD', 'Nord'
    NORD_OUEST = 'NORD_OUEST', 'Nord-Ouest'
    OUEST = 'OUEST', 'Ouest'
    SUD = 'SUD', 'Sud'
    SUD_OUEST = 'SUD_OUEST', 'Sud-Ouest'


class Niveau(models.TextChoices):
    L1 = 'L1', 'Licence 1'
    L2 = 'L2', 'Licence 2'
    L3 = 'L3', 'Licence 3'
    M1 = 'M1', 'Master 1'
    M2 = 'M2', 'Master 2'


class Etudiant(models.Model):
    matricule = models.CharField(max_length=50, primary_key=True)
    mot_de_passe = models.CharField(max_length=128, blank=True, default='')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100)
    region = models.CharField(max_length=20, choices=Region.choices)
    # Note : Le champ id_filiere (FK) sera lié lorsque l'app academic sera prête
    filiere = models.ForeignKey(
        'academic.Filiere',
        on_delete=models.CASCADE,
        related_name='etudiants',
        null=True,
        blank=True
    )
    niveau = models.CharField(max_length=2, choices=Niveau.choices)

    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenom}"


class Enseignant(models.Model):
    matricule = models.CharField(max_length=50, primary_key=True)
    mot_de_passe = models.CharField(max_length=128, blank=True, default='')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    fonction = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenom}"


