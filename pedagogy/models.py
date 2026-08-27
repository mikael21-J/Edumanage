from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Etudiant, Enseignant
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