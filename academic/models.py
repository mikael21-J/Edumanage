from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Niveau, Enseignant


class Semestre(models.TextChoices):
    S1 = 'S1', 'Semestre 1'
    S2 = 'S2', 'Semestre 2'



class Faculte(models.Model):
    code_fac = models.CharField(max_length=20, unique=True, help_text="Ex: FS, FALSH, FSEG")
    nom_fac = models.CharField(max_length=150, help_text="Ex: Faculté des Sciences")

    class Meta:
        verbose_name = "Faculté / Établissement"
        verbose_name_plural = "Facultés / Établissements"

    def __str__(self):
        return f"{self.code_fac} - {self.nom_fac}"


class Departement(models.Model):
    code_dept = models.CharField(max_length=20, unique=True, help_text="Ex: INFO, MATH, PHYS")
    nom_dept = models.CharField(max_length=150, help_text="Ex: Département d'Informatique")
    faculte = models.ForeignKey(Faculte, on_delete=models.CASCADE, related_name='departements')

    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"

    def __str__(self):
        return f"{self.code_dept} ({self.faculte.code_fac})"


class Filiere(models.Model):
    code_filiere = models.CharField(max_length=20, unique=True, help_text="Ex: ICT4D, INFO_LMD")
    nom_filiere = models.CharField(max_length=150)
    # Relation : Une filière appartient à un Département
    departement = models.ForeignKey(
        Departement, 
        on_delete=models.CASCADE, 
        related_name='filieres',
        null=True, 
        blank=True
    )

    class Meta:
        verbose_name = "Filière"
        verbose_name_plural = "Filières"

    def __str__(self):
        return f"{self.code_filiere} - {self.nom_filiere}"


class UE(models.Model):
    code_ue = models.CharField(max_length=20, primary_key=True, help_text="Ex: INF112")
    intitule = models.CharField(max_length=150)
    credits = models.PositiveIntegerField()
    avec_tp = models.BooleanField(default=False, verbose_name="Comporte des TP")
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='ues')
    niveau = models.CharField(max_length=2, choices=Niveau.choices)
    semestre = models.CharField(max_length=2, choices=Semestre.choices)
    # Nouveaux champs pour les pourcentages de notation
    pourcentage_cc = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Pourcentage Contrôle Continu (0-100)"
    )
    pourcentage_tp = models.PositiveIntegerField(
        default=20,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Pourcentage Travaux Pratiques (0-100)"
    )
    pourcentage_sn = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Pourcentage Session Normale (0-100)"
    )

    class Meta:
        verbose_name = "Unité d'Enseignement (UE)"
        verbose_name_plural = "Unités d'Enseignement (UE)"

    def clean(self):
        """Valider que la somme des pourcentages = 100"""
        total = self.pourcentage_cc + self.pourcentage_tp + self.pourcentage_sn
        if total != 100:
            raise ValidationError(
                f"La somme des pourcentages doit être 100. Actuellement: CC={self.pourcentage_cc}% + TP={self.pourcentage_tp}% + SN={self.pourcentage_sn}% = {total}%"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code_ue} : {self.intitule} ({self.niveau} - {self.filiere.code_filiere})"


class EnseignantUE(models.Model):
    """
    Déclaration des UE qu'un enseignant est habilité à dispenser.
    """
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE, related_name='declarations_ue')
    ue = models.ForeignKey(UE, on_delete=models.CASCADE, related_name='enseignants_habilites')
    date_declaration = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Habilitation Enseignant / UE"
        verbose_name_plural = "Habilitations Enseignants / UE"
        unique_together = ('enseignant', 'ue')

    def __str__(self):
        return f"{self.enseignant.nom} -> {self.ue.code_ue}"