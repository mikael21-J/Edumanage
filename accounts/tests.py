from django.test import TestCase
from django.urls import reverse

from academic.models import Departement, Faculte, Filiere, UE, EnseignantUE
from pedagogy.models import InscriptionUE, Note, PV, PVNote, Requete
from .models import AdminCellule, Etudiant, Enseignant


class NotesWorkflowTests(TestCase):
	def setUp(self):
		faculte = Faculte.objects.create(code_fac='FS', nom_fac='Sciences')
		departement = Departement.objects.create(code_dept='INFO', nom_dept='Informatique', faculte=faculte)
		filiere = Filiere.objects.create(code_filiere='INFO', nom_filiere='Informatique', departement=departement)
		self.ue = UE.objects.create(code_ue='INF101', intitule='Programmation', credits=6, avec_tp=True, filiere=filiere, niveau='L1', semestre='S1')
		self.enseignant = Enseignant.objects.create(matricule='ENS01', nom='Prof', prenom='Ada', fonction='Enseignant')
		self.admin = AdminCellule.objects.create(username='cellule', mot_de_passe='secret', nom='Admin', prenom='Cellule')
		EnseignantUE.objects.create(enseignant=self.enseignant, ue=self.ue)
		for index in range(2):
			student = Etudiant.objects.create(matricule=f'ETU{index}', nom='Nom', prenom=f'Etudiant{index}', date_naissance='2000-01-01', lieu_naissance='Yaoundé', region='CENTRE', filiere=filiere, niveau='L1')
			InscriptionUE.objects.create(etudiant=student, ue=self.ue)

	def authenticate(self, role, identifier):
		session = self.client.session
		session['auth_role'] = role
		session['auth_identifier'] = identifier
		session['auth_matricule'] = identifier
		session.save()

	def test_cc_and_sn_visibility_rules(self):
		self.authenticate('enseignant', self.enseignant.matricule)
		students = list(Etudiant.objects.all())
		self.client.post(reverse('teacher_gradebook', args=[self.ue.code_ue, 'CC']), {f'note_{student.matricule}': '12' for student in students})
		self.client.post(reverse('teacher_gradebook', args=[self.ue.code_ue, 'SN']), {f'note_{student.matricule}': '14' for student in students})
		self.assertTrue(Note.objects.filter(ue=self.ue, type_evaluation='CC', est_publie=True).count() == 2)
		self.assertTrue(Note.objects.filter(ue=self.ue, type_evaluation='SN', est_publie=False).count() == 2)

	def test_pv_snapshots_students_and_publishes_notes(self):
		self.authenticate('enseignant', self.enseignant.matricule)
		students = list(Etudiant.objects.all())
		for evaluation_type, value in (('CC', '12'), ('TP', '13'), ('SN', '14')):
			self.client.post(reverse('teacher_gradebook', args=[self.ue.code_ue, evaluation_type]), {f'note_{student.matricule}': value for student in students})
		response = self.client.post(reverse('teacher_pv', args=[self.ue.code_ue]), {'action': 'send'})
		self.assertRedirects(response, reverse('teacher_pv', args=[self.ue.code_ue]))
		pv = PV.objects.get(ue=self.ue)
		self.assertEqual(pv.etat, 'ENVOYE')
		self.assertEqual(PVNote.objects.filter(pv=pv).count(), 2)
		self.authenticate('admin_cellule', self.admin.username)
		self.client.post(reverse('admin_pv_detail', args=[pv.id]), {'action': 'publish'})
		self.assertEqual(PV.objects.get(pk=pv.id).etat, 'PUBLIE')
		self.assertEqual(Note.objects.filter(ue=self.ue, est_publie=True).count(), 6)

	def test_reject_returns_to_dashboard_and_hides_pv(self):
		pv = PV.objects.create(ue=self.ue, enseignant=self.enseignant, etat='ENVOYE')
		self.authenticate('admin_cellule', self.admin.username)
		response = self.client.post(reverse('admin_pv_detail', args=[pv.id]), {'action': 'reject', 'commentaire_rejet': 'Une note est à vérifier.'})
		self.assertRedirects(response, reverse('dashboard_admin_cellule'))
		self.assertEqual(PV.objects.get(pk=pv.id).etat, 'REJETE')
		dashboard = self.client.get(reverse('dashboard_admin_cellule'))
		self.assertNotContains(dashboard, self.ue.code_ue)

	def test_student_can_submit_one_request_for_published_note(self):
		student = Etudiant.objects.first()
		Note.objects.create(etudiant=student, ue=self.ue, type_evaluation='CC', valeur_note=12, est_publie=True)
		self.authenticate('etudiant', student.matricule)
		response = self.client.post(reverse('student_submit_requete', args=[self.ue.code_ue]), {'motif': 'ERREUR', 'type_evaluation': 'CC', 'description': 'La note semble incorrecte.'})
		self.assertRedirects(response, reverse('student_ue_detail', args=[self.ue.code_ue]))
		self.assertEqual(Requete.objects.filter(etudiant=student, ue=self.ue, type_evaluation='CC').count(), 1)
		response = self.client.post(reverse('student_submit_requete', args=[self.ue.code_ue]), {'motif': 'ERREUR', 'type_evaluation': 'CC', 'description': 'Deuxième demande.'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(Requete.objects.filter(etudiant=student, ue=self.ue, type_evaluation='CC').count(), 1)

	def test_teacher_validates_request_and_it_leaves_inbox(self):
		student = Etudiant.objects.first()
		requete = Requete.objects.create(etudiant=student, enseignant=self.enseignant, ue=self.ue, type_evaluation='CC', motif='ERREUR', description='Vérifier la note.')
		self.authenticate('enseignant', self.enseignant.matricule)
		response = self.client.post(reverse('teacher_requete_detail', args=[requete.id]), {'action': 'validate'})
		self.assertRedirects(response, reverse('teacher_requetes'))
		requete.refresh_from_db()
		self.assertEqual(requete.etat, 'VALIDEE')
		self.assertNotContains(self.client.get(reverse('teacher_requetes')), requete.ue.code_ue)
