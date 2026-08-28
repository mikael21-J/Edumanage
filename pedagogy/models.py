from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import AdminCellule, Etudiant, Enseignant
from academic.models import UE


class TypeEvaluation(models.TextChoices):
    CC = 'CC', 'Contrôle Continu'
    TP = 'TP', 'Travaux Pratiques'
    SN = 'SN', 'Session Normale'
    RAT = 'RAT', 'Rattrapage'


class InscriptionUE(models.Model):
    """
    Choix d'UE validé par l'étudiant lors de son inscription.
    """
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='inscriptions')
    ue = models.ForeignKey(UE, on_delete=models.CASCADE, related_name='inscriptions_etudiants')
    annee_academique = models.CharField(max_length=20, default='2025-2026')
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Inscription à une UE"
        verbose_name_plural = "Inscriptions aux UE"
        unique_together = ('etudiant', 'ue', 'annee_academique')

    def __str__(self):
        return f"{self.etudiant.matricule} -> {self.ue.code_ue} ({self.annee_academique})"


class Classe(models.Model):
    """
    Espace logique d'un cours attribué au premier enseignant disponible dans EnseignantUE.
    """
    ue = models.ForeignKey(UE, on_delete=models.CASCADE, related_name='classes')
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE, related_name='classes')
    annee_academique = models.CharField(max_length=20, default='2025-2026')

    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        unique_together = ('ue', 'annee_academique')

    def __str__(self):
        return f"{self.ue.filiere.code_filiere} {self.ue.niveau} - {self.ue.code_ue} ({self.enseignant.nom})"


class Note(models.Model):
    """
    Note individuelle par étudiant, par UE et par type d'évaluation.
    """
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='notes')
    ue = models.ForeignKey(UE, on_delete=models.CASCADE, related_name='notes')
    type_evaluation = models.CharField(max_length=3, choices=TypeEvaluation.choices)
    valeur_note = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00), MaxValueValidator(20.00)],
        help_text="Note comprise entre 0 et 20"
    )
    est_publie = models.BooleanField(default=False, verbose_name="Rendre visible à l'étudiant")

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        unique_together = ('etudiant', 'ue', 'type_evaluation')

    def __str__(self):
        statut = f"{self.valeur_note}/20" if self.est_publie else "NON PUBLIE (NONE)"
        return f"{self.etudiant.matricule} | {self.ue.code_ue} | {self.type_evaluation} : {statut}"


class EtatPV(models.TextChoices):
    BROUILLON = 'BROUILLON', 'Brouillon'
    ENVOYE = 'ENVOYE', 'Envoyé à la cellule'
    REJETE = 'REJETE', 'Rejeté'
    PUBLIE = 'PUBLIE', 'Publié'


class PV(models.Model):
    ue = models.ForeignKey(UE, on_delete=models.PROTECT, related_name='pvs')
    enseignant = models.ForeignKey(Enseignant, on_delete=models.PROTECT, related_name='pvs')
    annee_academique = models.CharField(max_length=20, default='2025-2026')
    etat = models.CharField(max_length=10, choices=EtatPV.choices, default=EtatPV.BROUILLON)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_envoi = models.DateTimeField(null=True, blank=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    admin_traitement = models.ForeignKey(
        AdminCellule, null=True, blank=True, on_delete=models.PROTECT, related_name='pvs_traites'
    )
    commentaire_rejet = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Procès-verbal'
        verbose_name_plural = 'Procès-verbaux'
        constraints = [
            models.UniqueConstraint(fields=('ue', 'annee_academique'), name='unique_pv_ue_annee')
        ]
        ordering = ('-date_envoi', '-date_creation')

    def __str__(self):
        return f"PV {self.ue.code_ue} - {self.annee_academique} ({self.etat})"


class PVNote(models.Model):
    pv = models.ForeignKey(PV, on_delete=models.CASCADE, related_name='lignes')
    etudiant = models.ForeignKey(Etudiant, on_delete=models.PROTECT, related_name='lignes_pv')
    cc = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    tp = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    sn = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Ligne de PV'
        verbose_name_plural = 'Lignes de PV'
        constraints = [
            models.UniqueConstraint(fields=('pv', 'etudiant'), name='unique_pv_etudiant')
        ]

    def __str__(self):
        return f"{self.pv.ue.code_ue} - {self.etudiant.matricule}"


class MotifRequete(models.TextChoices):
    ABSENCE = 'ABSENCE', 'Absence de note'
    NON_MERITEE = 'NON_MERITEE', 'Note non méritée'
    ERREUR = 'ERREUR', 'Erreur de note'


class EtatRequete(models.TextChoices):
    ENVOYEE = 'ENVOYEE', 'Envoyée'
    VALIDEE = 'VALIDEE', 'Validée'


class Requete(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='requetes')
    enseignant = models.ForeignKey(Enseignant, on_delete=models.PROTECT, related_name='requetes_recues')
    ue = models.ForeignKey(UE, on_delete=models.PROTECT, related_name='requetes')
    type_evaluation = models.CharField(max_length=3, choices=TypeEvaluation.choices)
    motif = models.CharField(max_length=20, choices=MotifRequete.choices)
    description = models.TextField()
    etat = models.CharField(max_length=10, choices=EtatRequete.choices, default=EtatRequete.ENVOYEE)
    date_envoi = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Requête étudiant'
        verbose_name_plural = 'Requêtes étudiants'
        constraints = [
            models.UniqueConstraint(
                fields=('etudiant', 'ue', 'type_evaluation'), name='unique_requete_note_etudiant'
            )
        ]
        ordering = ('-date_envoi',)

    def __str__(self):
        return f"{self.etudiant.matricule} - {self.ue.code_ue} - {self.type_evaluation}"