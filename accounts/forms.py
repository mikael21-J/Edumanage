from django import forms
from django.contrib.auth.hashers import make_password

from academic.models import UE
from pedagogy.models import MotifRequete, Requete, TypeEvaluation
from .models import Etudiant, Enseignant


class UEForm(forms.ModelForm):
    class Meta:
        model = UE
        fields = ('code_ue', 'intitule', 'credits', 'avec_tp', 'filiere', 'niveau', 'semestre', 'pourcentage_cc', 'pourcentage_tp', 'pourcentage_sn')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control form-control-sm'
        # Ajouter des attributs spécifiques pour les pourcentages
        self.fields['pourcentage_cc'].help_text = 'Pourcentage pour Contrôle Continu (défaut: 30%)'
        self.fields['pourcentage_tp'].help_text = 'Pourcentage pour Travaux Pratiques (défaut: 20%)'
        self.fields['pourcentage_sn'].help_text = 'Pourcentage pour Session Normale (défaut: 50%)'
        self.fields['pourcentage_cc'].widget.attrs['min'] = '0'
        self.fields['pourcentage_cc'].widget.attrs['max'] = '100'
        self.fields['pourcentage_tp'].widget.attrs['min'] = '0'
        self.fields['pourcentage_tp'].widget.attrs['max'] = '100'
        self.fields['pourcentage_sn'].widget.attrs['min'] = '0'
        self.fields['pourcentage_sn'].widget.attrs['max'] = '100'

    def clean(self):
        cleaned_data = super().clean()
        cc = cleaned_data.get('pourcentage_cc')
        tp = cleaned_data.get('pourcentage_tp')
        sn = cleaned_data.get('pourcentage_sn')
        
        if cc is not None and tp is not None and sn is not None:
            total = cc + tp + sn
            if total != 100:
                raise forms.ValidationError(
                    f'La somme des pourcentages doit être 100. Actuellement: {cc}% + {tp}% + {sn}% = {total}%'
                )


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
