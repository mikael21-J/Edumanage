from django import forms
from django.contrib.auth.hashers import make_password

from academic.models import UE
from pedagogy.models import MotifRequete, Requete, TypeEvaluation
from .models import Etudiant, Enseignant


class UEForm(forms.ModelForm):
    class Meta:
        model = UE
        fields = ('code_ue', 'intitule', 'credits', 'avec_tp', 'filiere', 'niveau', 'semestre')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control form-control-sm'


class EnseignantForm(forms.ModelForm):
    mot_de_passe = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Enseignant
        fields = ('matricule', 'nom', 'prenom', 'fonction', 'mot_de_passe')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control form-control-sm'

    def save(self, commit=True):
        instance = super().save(commit=False)
        password = self.cleaned_data.get('mot_de_passe')
        if password:
            instance.mot_de_passe = make_password(password)
        if commit:
            instance.save()
        return instance


class EtudiantForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        exclude = ('mot_de_passe',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control form-control-sm'


class RequeteForm(forms.ModelForm):
    type_evaluation = forms.ChoiceField(choices=(), label='Évaluation')

    class Meta:
        model = Requete
        fields = ('motif', 'type_evaluation', 'description')
        labels = {'motif': 'Motif', 'description': 'Description du problème'}
        widgets = {'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Décrivez brièvement le problème rencontré.'})}

    def __init__(self, *args, published_types=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['motif'].choices = MotifRequete.choices
        self.fields['type_evaluation'].choices = published_types or TypeEvaluation.choices
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control form-control-sm'
